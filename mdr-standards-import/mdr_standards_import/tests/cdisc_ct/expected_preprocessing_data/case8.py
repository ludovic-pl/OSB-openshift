from mdr_standards_import.scripts.load_ct_preprocessing import Term, Codelist
from mdr_standards_import.tests.cdisc_ct.test_pipeline import Package, Import, Log


def get_expected_imports(effective_date, author_id):
    term1_a = Term(
        uid=f"{effective_date}_T1_sv-T1-1",
        concept_id="T1_sv-T1-1",
        code_submission_value="sv-T1-1",
        name_submission_value=None,
        submission_value=None,
        preferred_term="PT T1",
        definition="Definition T1",
        synonyms=None,
    )
    term1_b = Term(
        uid=f"{effective_date}_T1_sv-T1-2",
        concept_id="T1_sv-T1-2",
        code_submission_value="sv-T1-2",
        name_submission_value=None,
        submission_value=None,
        preferred_term="PT T1",
        definition="Definition T1",
        synonyms=None,
    )
    term1_c = Term(
        uid=f"{effective_date}_T1_sv-T1-3",
        concept_id="T1_sv-T1-3",
        code_submission_value="sv-T1-3",
        name_submission_value=None,
        submission_value=None,
        preferred_term="PT T1",
        definition="Definition T1",
        synonyms=None,
    )

    codelist1 = Codelist(
        uid=f"{effective_date}_C1A",
        concept_id="C1A",
        name="Codelist 1A",
        submission_value="SV",
        preferred_term="PT 1A",
        definition="Definition 1A",
        extensible=True,
        synonyms=None,
        terms=[term1_a],
    )

    codelist2 = Codelist(
        uid=f"{effective_date}_C1B",
        concept_id="C1B",
        name="Codelist 1B",
        submission_value="SV",
        preferred_term="PT 1B",
        definition="Definition 1B",
        extensible=True,
        synonyms=None,
        terms=[term1_b],
    )

    codelist3 = Codelist(
        uid=f"{effective_date}_C1C",
        concept_id="C1C",
        name="Codelist 1C",
        submission_value="SV",
        preferred_term="PT 1C",
        definition="Definition 1C",
        extensible=True,
        synonyms=None,
        terms=[term1_c],
    )

    term2 = Term(
        uid=f"{effective_date}_T2",
        concept_id="T2",
        code_submission_value=None,
        name_submission_value=None,
        submission_value=None,
        preferred_term="PT T2",
        definition="Definition T2",
        synonyms=None,
    )
    codelist4 = Codelist(
        uid=f"{effective_date}_C2",
        concept_id="C2",
        name="Codelist 2",
        submission_value="SV",
        preferred_term="PT 2",
        definition="Definition 2",
        extensible=True,
        synonyms=None,
        terms=[term2],
    )

    package1 = Package(
        uid=f"{effective_date}_TEST-CASE 8 CT",
        catalogue_name="TEST-CASE 8 CT",
        registration_status="Testing",
        name="TEST-CASE 8 CT 2020-01-01",
        label="Test-Case 8 Controlled Terminology Package 1 Effective 2020-01-01",
        description="Test-Case 8: a) there are three submission values for the same term T1 and b) there is no submission value for T2 -> log as inconsistency.",
        source="Test source",
        href="/mdr/ct/packages/cat8-2020-01-01",
        terms=[term1_a, term1_b, term1_c, term2],
        codelists=[codelist1, codelist2, codelist3, codelist4],
        discontinued_codelists=[],
    )

    warning1 = Log(
        level="Warning",
        tagline="no term submission value",
        message="",
        affected_uid=f"{effective_date}_T2",
    )

    import1 = Import(
        effective_date=effective_date,
        author_id=author_id,
        packages=[package1],
        discontinued_codelists=[],
        log_entries=[warning1],
    )

    return [import1]
