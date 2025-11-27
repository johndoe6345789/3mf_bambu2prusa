import os
import zipfile

import lxml.etree as ET

from bambu_to_prusa.converter import BambuToPrusaConverter
from bambu_to_prusa.model_processing import DEFAULT_TRANSFORM, MODEL_NAMESPACE, SLIC3R_NAMESPACE

SAMPLE_XML = """<?xml version='1.0' encoding='UTF-16'?>
<model xmlns="http://example.com" p:UUID="123" paint_color="abc" paint_seam="EDGE">
  <resources>
    <object id="1" type="model"><mesh /></object>
  </resources>
</model>
"""

BAMBU_MODEL_XML = """<?xml version='1.0' encoding='UTF-8'?>
<model xmlns="http://www.bambulab.com/schemas/3mf/2023" xmlns:p="http://schemas.microsoft.com/packaging/2006/relationships" p:UUID="bambu-test-uuid" paint_color="ff0000" paint_seam="EDGE">
  <metadata xml:lang="en-US" name="Title">Bambu Test Model</metadata>
  <resources>
    <object id="1" type="model">
      <mesh>
        <vertices>
          <vertex x="0" y="0" z="0" />
          <vertex x="1" y="0" z="0" />
          <vertex x="0" y="1" z="0" />
        </vertices>
        <triangles>
          <triangle v1="0" v2="1" v3="2" />
        </triangles>
      </mesh>
    </object>
    <object id="2" type="support" />
  </resources>
  <build>
    <item objectid="1" transform="1 0 0 0 1 0 0 0 1 0 0 0" />
    <item objectid="2" />
  </build>
</model>
"""

BAMBU_CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml" />
  <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml" />
</Types>
"""

BAMBU_RELS = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Target="/3D/Objects/bambu.model" Id="rel-1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/3dmodel" />
</Relationships>
"""


def create_sample_archive(tmp_path):
    input_dir = tmp_path / "input"
    objects_dir = input_dir / "3D" / "Objects"
    objects_dir.mkdir(parents=True)
    (objects_dir / "test.model").write_text(SAMPLE_XML, encoding="utf-8")

    archive_path = tmp_path / "sample.3mf"
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for folder, _, files in os.walk(input_dir):
            for filename in files:
                file_path = os.path.join(folder, filename)
                arcname = os.path.relpath(file_path, input_dir)
                archive.write(file_path, arcname)
    return archive_path


def test_convert_archive_produces_prusa_zip(tmp_path):
    archive_path = create_sample_archive(tmp_path)
    output_path = tmp_path / "output.3mf"

    converter = BambuToPrusaConverter()
    converter.convert_archive(str(archive_path), str(output_path))

    assert output_path.exists()
    with zipfile.ZipFile(output_path, "r") as output_zip:
        names = output_zip.namelist()
        assert any(name.endswith("3D/Objects/test.model") for name in names)
        assert "_rels/.rels" in names

        with output_zip.open("3D/Objects/test.model") as model_file:
            model_content = model_file.read()
            model_root = ET.fromstring(model_content)
            assert model_root.findall(".//{*}object")


def create_valid_bambu_archive(tmp_path):
    input_dir = tmp_path / "bambu"
    objects_dir = input_dir / "3D" / "Objects"
    rels_dir = input_dir / "_rels"

    objects_dir.mkdir(parents=True)
    rels_dir.mkdir(parents=True)

    (objects_dir / "bambu.model").write_text(BAMBU_MODEL_XML, encoding="utf-8")
    (rels_dir / ".rels").write_text(BAMBU_RELS, encoding="utf-8")
    (input_dir / "[Content_Types].xml").write_text(BAMBU_CONTENT_TYPES, encoding="utf-8")

    archive_path = tmp_path / "bambu.3mf"
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for folder, _, files in os.walk(input_dir):
            for filename in files:
                file_path = os.path.join(folder, filename)
                archive.write(file_path, os.path.relpath(file_path, input_dir))
    return archive_path


def test_end_to_end_bambu_to_prusa_conversion(tmp_path):
    bambu_archive = create_valid_bambu_archive(tmp_path)
    output_path = tmp_path / "prusa.3mf"

    with zipfile.ZipFile(bambu_archive, "r") as bambu_zip:
        bambu_files = set(bambu_zip.namelist())
        assert {"[Content_Types].xml", "_rels/.rels", "3D/Objects/bambu.model"}.issubset(bambu_files)

        model_tree = ET.fromstring(bambu_zip.read("3D/Objects/bambu.model"))
        assert model_tree.attrib["{http://schemas.microsoft.com/packaging/2006/relationships}UUID"] == "bambu-test-uuid"
        assert model_tree.attrib["paint_color"] == "ff0000"
        assert model_tree.find(".//{*}object[@id='2']").attrib["type"] == "support"

    converter = BambuToPrusaConverter()
    converter.convert_archive(str(bambu_archive), str(output_path))

    with zipfile.ZipFile(output_path, "r") as prusa_zip:
        output_files = set(prusa_zip.namelist())
        assert {"[Content_Types].xml", "_rels/.rels", "3D/Objects/bambu.model"}.issubset(output_files)

        rels_tree = ET.fromstring(prusa_zip.read("_rels/.rels"))
        relationships = rels_tree.findall("{http://schemas.openxmlformats.org/package/2006/relationships}Relationship")
        assert relationships
        assert relationships[0].attrib["Target"] == "/3D/Objects/bambu.model"

        model_root = ET.fromstring(prusa_zip.read("3D/Objects/bambu.model"))
        assert model_root.tag == f"{{{MODEL_NAMESPACE}}}model"
        assert model_root.nsmap[None] == MODEL_NAMESPACE
        assert model_root.nsmap.get("slic3rpe") == SLIC3R_NAMESPACE

        objects = model_root.findall(".//{*}resources/{*}object")
        assert len(objects) == 1
        assert objects[0].attrib["id"] == "1"
        assert objects[0].find(".//{*}mesh/{*}triangles/{*}triangle") is not None

        build_items = model_root.findall(".//{*}build/{*}item")
        assert len(build_items) == 1
        assert build_items[0].attrib["transform"] == DEFAULT_TRANSFORM

        content = prusa_zip.read("3D/Objects/bambu.model").decode("utf-8")
        assert "paint_color" not in content
        assert "paint_seam" not in content
