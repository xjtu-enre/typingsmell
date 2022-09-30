from pathlib import Path
from algorithm.profiler.api import get_typing_practice
from algorithm.TypingCoverageDetection.CsvItem import CsvItem, union_csv_items
from algorithm.TypingCoverageDetection.filecoveragecalculator import ProjeceName
from algorithm.TypingCoverageDetection.typingImportCounter import TypingDepsCounter


class Res:
    def __init__(self, project_path, stub_path, entities):
        self.project_path = project_path
        self.stub_path = stub_path
        self.entities = entities


class Pattern:
    project_path = './assets/projects/'
    output_path = "./assets/calculation/"

    @classmethod
    def get_pattern(cls, project_name, stub):
        print(f"\nstart checking project {project_name} pattern")
        project_path = Path(cls.project_path + project_name)
        stub_path = Path(cls.project_path + stub)
        pattern_count, pattern_info = get_typing_practice(cls.output_path + project_name, project_path, stub_path)
        print(f"\nend checking project {project_name} pattern")
        return pattern_count, pattern_info

    @classmethod
    def get_usage(cls, project_name, stub):
        print(f"\nstart checking project {project_name} usage")
        project_path = Path(cls.project_path + project_name)
        stub_path = Path(cls.project_path + stub)
        project_name_item = ProjeceName(project_name)
        tdc = TypingDepsCounter(project_path.parent)
        tdc.cal_import_deps(project_path, stub_path)
        usage = tdc.get_import_deps()
        with open(cls.output_path + project_name + "/ImportDependency.csv", "w") as file:
            file.write(union_csv_items(project_name_item, usage))

        print(f"project {project_name} checked")
        return tdc.get_usage()
