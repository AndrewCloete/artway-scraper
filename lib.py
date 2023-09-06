import re


def best_effort_title_parse(full_title_string):
    if " - VM - " in full_title_string:
        result = re.search(r"(.*) - VM - (.*)", full_title_string)
        if len(result.groups()) == 2:
            (title, author) = result.groups()
            return {"title": title, "author": author, "vm": True}
    if " - BM - " in full_title_string:
        result = re.search(r"(.*) - BM - (.*)", full_title_string)
        if len(result.groups()) == 2:
            (title, author) = result.groups()
            return {"title": title, "author": author, "vm": True}
    if " - by " in full_title_string:
        result = re.search(r"(.*) - by (.*)", full_title_string)
        if len(result.groups()) == 2:
            (title, author) = result.groups()
            return {"title": title, "author": author}
    if " - " in full_title_string:
        result = re.search(r".* - (.*)", full_title_string)
        if len(result.groups()) == 1:
            author = result.groups()[0]
            return {"title": full_title_string, "author": author}
    return {"title": full_title_string}


if __name__ == "__main__":
    tests = [
        "Abramishvili, Merab - VM - Anna Mgaloblishvili",
        "Arcabas - and Jacques Maritain - by David Jeffrey",
        "Arcabas - VM - Kirstin Jeffrey Johnson",
        "Armando - VM - Anne Marijke Spijkerboer",
        "Aldrich, Lynn: Three Founts",
        "Alkema, Josefien",
        "Altdorfer, Albrecht - by H.R. Rookmaaker",
        "Alvarez, Claudia - VM - Steve Scott",
        "Ana Maria Pacheco - VM - Jonathan Evens",
        "Anderson, Chris - by Gina Bria",
    ]
    for test in tests:
        result = best_effort_title_parse(test)
        print(result)
