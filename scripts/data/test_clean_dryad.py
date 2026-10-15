"""Regression tests for offline Dryad normalization and package boundaries."""
import json
import contextlib
import io
import tempfile
import unittest
import zipfile
from pathlib import Path

from clean_dryad import decimal_token, header, normalize, run, table, workbook, xml
from clean_plantexpert import snapshot, write_json

CONFIG = json.loads(Path(__file__).with_name("dryad-config.json").read_text(encoding="utf-8"))


def cell(value=None, kind="numeric", formula=None, ref="B3"):
    return {"coordinate":ref,"raw_kind":kind,"raw_value":value,"formula":formula}


class DryadTests(unittest.TestCase):
    def test_zero_precision_and_nonfinite(self):
        for value in ("0.0","0.021135","3.51089241182757","-2.0","1e-9"):
            self.assertEqual(normalize(cell(value),"numeric")["value"],value)
        for value in ("NaN","Infinity","1_000"," 0.0","1,2"):
            with self.assertRaises(ValueError): decimal_token(value)

    def test_formula_cache_not_measured_value(self):
        formula = {"raw_expression":"U3/V3","attributes":{},"shared_base":None}
        result = normalize(cell("5.52758298914368",formula=formula),"numeric")
        self.assertIsNone(result["value"])
        self.assertEqual(result["cached_value"],"5.52758298914368")
        self.assertEqual(result["formula"],formula)
        self.assertEqual(result["kind"],"formula")
        empty = normalize(cell(formula=formula),"numeric")
        self.assertEqual(empty["kind"],"formula")
        self.assertIsNone(empty["cached_value"])
        self.assertEqual(normalize(cell(),"numeric")["kind"],"missing")

    def test_date_status_and_opaque_id(self):
        self.assertEqual(normalize(cell("T1-1-1","text"),"opaque_id")["value"],"T1-1-1")
        self.assertEqual(normalize(cell("yes","text"),"irrigation_status")["value"],True)
        self.assertEqual(normalize(cell("No","text"),"irrigation_status")["value"],False)
        self.assertEqual(normalize(cell("2024-04-01","text"),"calendar_date")["value"],"2024-04-01")
        for kind,value in (("calendar_date","2024-02-30"),("calendar_date","2024/04/01"),("irrigation_status","maybe")):
            with self.assertRaises(ValueError): normalize(cell(value,"text"),kind)

    def test_merged_header_provenance(self):
        sheet = {"merged_ranges":["A1:H1"],"cells":{"A1":cell("Soluble Solids","text",ref="A1")}}
        self.assertEqual(header(sheet,"H1"),{"source_cell":"H1","merged_anchor":"A1","value":"Soluble Solids"})

    def test_header_mismatch_is_blocked(self):
        sheet = {"merged_ranges":[],"cells":{"A2":cell("unknown","text",ref="A2")}}
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError,"header mismatch"):
                table(CONFIG["tables"][0],sheet,"test-hash",Path(folder))

    def test_no_silent_merge_of_duplicate_ids(self):
        spec = {"id":"test","file":"test.xlsx","sheet":"Sheet1","header_rows":[1],"first_row":2,"last_row":3,
                "columns":["A","B"],"key":"A","key_type":"opaque_id","header_guards":{"A1":"Code"}}
        sheet = {"merged_ranges":[],"cells":{"A1":cell("Code","text",ref="A1"),"B1":cell("mass(g)","text",ref="B1"),
                 "A2":cell("T1-1","text",ref="A2"),"A3":cell("T1-1","text",ref="A3"),"B2":cell("0.0",ref="B2"),"B3":cell("0.0",ref="B3")}}
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder); (target/"tables").mkdir()
            summary, records, manifest, queue, fields = table(spec,sheet,"test-hash",target)
            self.assertEqual(summary["retained_records"],2)
            self.assertEqual(summary["excluded_records"],0)
            self.assertEqual(summary["field_counts"]["zero_numeric_preserved"],2)
            self.assertEqual(len({r["record_id"] for r in records}),2)
            self.assertIn("duplicate_original_key_retained",{q["reason"] for q in queue})
            self.assertIn("repeated_measurement_vector_retained",{q["reason"] for q in queue})
            self.assertTrue(all(r["treatment_id"] is None and not r["training_ready"] for r in records))
            self.assertEqual(manifest[1]["source_row"],3)
            self.assertEqual(fields[1]["unit_tokens_from_header"],["g"])

    def test_dtd_and_unsafe_package(self):
        with self.assertRaises(ValueError): xml(b'<!DOCTYPE x [<!ENTITY a "x">]><x/>')
        with self.assertRaises(ValueError): xml('<!DOCTYPE x [<!ENTITY a "x">]><x/>'.encode("utf-16"))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/"bad.xlsx"
            with zipfile.ZipFile(path,"w") as archive: archive.writestr("../escape.xml","<x/>")
            with self.assertRaisesRegex(ValueError,"unsafe"): workbook(path,CONFIG)

    def test_part_resource_limit_and_macro(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/"bad.xlsx"
            with zipfile.ZipFile(path,"w") as archive: archive.writestr("large.xml","a"*100)
            with self.assertRaisesRegex(ValueError,"part limit"): workbook(path,{**CONFIG,"maximum_part_bytes":10})
            with zipfile.ZipFile(path,"w") as archive: archive.writestr("xl/vbaProject.bin",b"no execution")
            with self.assertRaisesRegex(ValueError,"macro"): workbook(path,CONFIG)

    def test_shared_formula_follower_and_whitespace(self):
        main = '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="leaf " sheetId="1" r:id="r1"/></sheets></workbook>'
        rel = '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="r1" Target="worksheets/sheet1.xml"/></Relationships>'
        sheet = '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><dimension ref="A1:XFD100"/><sheetData><row r="1"><c r="A1"><f t="shared" si="0" ref="A1:A2">B1*G1</f><v>0</v></c><c r="S1" t="inlineStr"><is><t xml:space="preserve"> </t></is></c><c r="XFD1" s="1"/></row><row r="2"><c r="A2"><f t="shared" si="0"/><v>1.23456789012345</v></c></row></sheetData></worksheet>'
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/"test.xlsx"
            with zipfile.ZipFile(path,"w") as archive:
                for name,body in (("xl/workbook.xml",main),("xl/_rels/workbook.xml.rels",rel),("xl/worksheets/sheet1.xml",sheet)): archive.writestr(name,body)
            books,_ = workbook(path,CONFIG)
            cells = books["leaf "]["cells"]
            self.assertEqual(len(cells),4)
            self.assertEqual(cells["S1"]["raw_value"]," ")
            self.assertIsNone(cells["XFD1"]["raw_value"])
            follower = normalize(cells["A2"],"numeric")
            self.assertIsNone(follower["formula"]["raw_expression"])
            self.assertEqual(follower["formula"]["shared_base"]["coordinate"],"A1")
            self.assertEqual(follower["cached_value"],"1.23456789012345")

    def fixture_project(self, folder):
        project = Path(folder)
        source = project/"raw/fixture"; source.mkdir(parents=True)
        (source/"README.md").write_text("Fixture only; not Dryad data.",encoding="utf-8")
        import openpyxl
        book = openpyxl.Workbook()
        sheet = book.active; sheet.title = "Sheet1"
        sheet.append(["Code","mass(g)"]); sheet.append(["T1-1",0]); sheet.append(["T1-1",2.0])
        book.save(source/"test.xlsx"); book.close()
        write_json(project/"intake.json",{"files":[{"dataset":"fixture","relative_path":"fixture/"+r["source_file"],"bytes":r["bytes"],"sha256":r["sha256"]} for r in snapshot(source)]})
        config = {**CONFIG,"source_root":"raw/fixture","processed_parent":"processed","report_parent":"reports", "intake_manifest":"intake.json","reference_inputs":[],
            "tables":[{"id":"test","file":"test.xlsx","sheet":"Sheet1","header_rows":[1],"first_row":2,"last_row":3,
                       "columns":["A","B"],"key":"A","key_type":"opaque_id","header_guards":{"A1":"Code"}}]}
        path = project/"config.json"; write_json(path,config)
        return project,source,path,config

    def test_versioned_idempotency_and_tamper_refusal(self):
        with tempfile.TemporaryDirectory() as folder, contextlib.redirect_stdout(io.StringIO()):
            project,source,path,_ = self.fixture_project(folder)
            before = snapshot(source)
            result = run(path,project)
            output = project/"processed"/result["run_id"]
            report = project/"reports"/result["run_id"]
            hashes = (snapshot(output),snapshot(report))
            repeated = run(path,project)
            self.assertEqual(result,repeated)
            self.assertEqual(hashes,(snapshot(output),snapshot(report)))
            self.assertEqual(result["retained_table_records"],2)
            self.assertEqual(result["source_physical_rows"],2)
            self.assertEqual(snapshot(source),before)
            target = output/"tables/test.jsonl"
            target.write_text(target.read_text(encoding="utf-8")+"\n",encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"hash changed"): run(path,project)

    def test_partial_checkpoint_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as folder, contextlib.redirect_stdout(io.StringIO()):
            project,source,path,config = self.fixture_project(folder)
            config["tables"][0]["header_guards"]["A1"] = "Wrong"
            write_json(path,config)
            before = snapshot(source)
            with self.assertRaisesRegex(ValueError,"header mismatch"): run(path,project)
            checkpoint = next((project/"reports").glob("*/checkpoint.json"))
            saved = checkpoint.read_bytes()
            self.assertEqual(json.loads(saved)["status"],"partial_failed_retained")
            with self.assertRaisesRegex(ValueError,"partial run retained"): run(path,project)
            self.assertEqual(checkpoint.read_bytes(),saved)
            self.assertEqual(snapshot(source),before)

    def test_output_cannot_be_any_raw_directory(self):
        with tempfile.TemporaryDirectory() as folder, contextlib.redirect_stdout(io.StringIO()):
            project,_,path,config = self.fixture_project(folder)
            config["processed_parent"] = "raw/other"
            write_json(path,config)
            with self.assertRaisesRegex(ValueError,"output overlaps"): run(path,project)
            self.assertFalse((project/"raw/other").exists())


if __name__ == "__main__": unittest.main()
