"""Boundary, preservation and end-to-end regression checks for Mendeley derivation."""
import contextlib
import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

from clean_mendeley import NumberLexeme, field, parse_array, process, run
from clean_plantexpert import snapshot, write_json

CONFIG=json.loads(Path(__file__).with_name("mendeley-config.json").read_text(encoding="utf-8"))


class MendeleyTests(unittest.TestCase):
    def test_exact_number_tokens_and_string_distinction(self):
        rows=parse_array('[{"n":0.0,"p":0.013930559788011455,"s":"0.0"}]',10)
        value,raw,start,end=rows[0]
        self.assertIsInstance(value["n"],NumberLexeme)
        self.assertNotIsInstance(value["s"],NumberLexeme)
        result=field(value["p"],"number",CONFIG["missing_tokens"])
        self.assertEqual(result["raw_value"],"0.013930559788011455")
        self.assertEqual(result["value"],"0.013930559788011455")
        self.assertEqual(field(value["n"],"number",CONFIG["missing_tokens"])["value"],"0.0")
        self.assertEqual(raw,'{"n":0.0,"p":0.013930559788011455,"s":"0.0"}')

    def test_missing_not_zero_and_invalid_numeric(self):
        for value in (None,"","NaN","NA"):
            self.assertEqual(field(value,"number",CONFIG["missing_tokens"])["kind"],"missing")
        self.assertEqual(field("0","number",CONFIG["missing_tokens"])["kind"],"decimal_text")
        for value in ("Infinity","1_000","abc",True):
            with self.assertRaises(ValueError): field(value,"number",CONFIG["missing_tokens"])

    def test_json_strictness_and_limit(self):
        for source in ('[{"x":1,"x":2}]','[{"x":NaN}]','[{}] trailing','[{},]','{}','[{}\u00a0]'):
            with self.assertRaises(ValueError): parse_array(source,10)
        self.assertEqual(parse_array(' [] ',10),[])
        with self.assertRaisesRegex(ValueError,"record limit"): parse_array('[{},{}]',1)

    def test_naive_timestamp_and_nfc(self):
        result=field("2023-07-27 17:50:10","timestamp",[])
        self.assertEqual(result["value"],"2023-07-27T17:50:10")
        self.assertNotIn("Z",result["value"])
        with self.assertRaises(ValueError): field("2023-02-30 17:50:10","timestamp",[])
        with self.assertRaises(ValueError): field("2023-07-27 17:50:10+05:30","timestamp",[])
        self.assertEqual(field(" e\u0301 ","category",[])["value"],"é")

    def fixture(self,folder):
        project=Path(folder);source=project/"raw/fixture";source.mkdir(parents=True)
        with (source/CONFIG["csv_file"]).open("w",encoding="utf-8",newline="") as stream:
            writer=csv.writer(stream);writer.writerow(CONFIG["csv_headers_expected"])
            row=["1"]*14;row[6]="Initial Stage";writer.writerow(row);writer.writerow(row)
        item={k:1 for k in CONFIG["json_keys_expected"]};item["dateTimeAdded"]="2023-07-27 17:50:10"
        (source/CONFIG["json_file"]).write_text(json.dumps([item,item]),encoding="utf-8")
        config={**CONFIG,"source_root":"raw/fixture","processed_parent":"processed","report_parent":"reports","intake_manifest":"intake.json","reference_inputs":[]}
        path=project/"config.json";write_json(path,config)
        self.intake(project,source)
        return project,source,path,config

    def intake(self,project,source):
        write_json(project/"intake.json",{"files":[{"dataset":"fixture","relative_path":"fixture/"+r["source_file"],"bytes":r["bytes"],"sha256":r["sha256"]} for r in snapshot(source)]})

    def test_preservation_duplicates_idempotency_tamper_and_no_join(self):
        with tempfile.TemporaryDirectory() as folder,contextlib.redirect_stdout(io.StringIO()):
            project,source,path,_=self.fixture(folder)
            before=snapshot(source);summary=run(path,project)
            self.assertEqual(summary["source_records"],4)
            self.assertEqual(summary["retained_records"],4)
            self.assertEqual(summary["excluded_records"],0)
            processed=project/"processed"/summary["run_id"];report=project/"reports"/summary["run_id"]
            saved=(snapshot(processed),snapshot(report))
            self.assertEqual(run(path,project),summary)
            self.assertEqual(saved,(snapshot(processed),snapshot(report)))
            self.assertEqual(snapshot(source),before)
            records=[json.loads(line) for line in (processed/"tables/json.jsonl").read_text().splitlines()]
            self.assertEqual(len(records),2)
            self.assertTrue(all(r["experimental_group"] is None and r["verified_cross_dataset_key"] is None and not r["training_ready"] for r in records))
            self.assertEqual(records[1]["source_pointer"],"/1")
            target=processed/"tables/json.jsonl";target.write_text(target.read_text()+"\n")
            with self.assertRaisesRegex(ValueError,"hash changed"): run(path,project)

    def test_schema_blocked_file_does_not_block_other_format(self):
        with tempfile.TemporaryDirectory() as folder,contextlib.redirect_stdout(io.StringIO()):
            project,source,path,_=self.fixture(folder)
            target=source/CONFIG["csv_file"]
            target.write_text("Wrong,Header\n1,2\n",encoding="utf-8")
            self.intake(project,source)
            before=snapshot(source);result=run(path,project)
            self.assertEqual(result["tables_completed"],1)
            self.assertEqual(result["retained_records"],2)
            self.assertTrue(result["status"].startswith("technical_partial"))
            self.assertEqual(result["blocked_files"][0]["table"],"csv")
            self.assertEqual(snapshot(source),before)

    def test_bad_row_quarantined_without_loss(self):
        with tempfile.TemporaryDirectory() as folder,contextlib.redirect_stdout(io.StringIO()):
            project,source,path,_=self.fixture(folder)
            with (source/CONFIG["csv_file"]).open("a",encoding="utf-8") as stream: stream.write("bad,row\n")
            target=source/CONFIG["json_file"]
            items=json.loads(target.read_text());items.append({"unknown":1});target.write_text(json.dumps(items))
            self.intake(project,source);result=run(path,project)
            self.assertEqual(result["source_records"],6)
            self.assertEqual(result["retained_records"],4)
            self.assertEqual(result["quarantined_records"],2)
            processed=project/"processed"/result["run_id"]
            csv_bad=json.loads((processed/"quarantine/csv.jsonl").read_text())
            json_bad=json.loads((processed/"quarantine/json.jsonl").read_text())
            self.assertEqual(csv_bad["raw_fields"],["bad","row"])
            self.assertEqual(json.loads(json_bad["raw_json_record"]),{"unknown":1})

    def test_output_and_source_guards(self):
        with tempfile.TemporaryDirectory() as folder,contextlib.redirect_stdout(io.StringIO()):
            project,source,path,config=self.fixture(folder)
            config["processed_parent"]="raw/other";write_json(path,config)
            with self.assertRaisesRegex(ValueError,"output overlaps"): run(path,project)
            config["processed_parent"]="processed";write_json(path,config)
            target=source/CONFIG["json_file"];target.write_text("[]")
            with self.assertRaisesRegex(ValueError,"immutable intake"): run(path,project)


if __name__=="__main__": unittest.main()
