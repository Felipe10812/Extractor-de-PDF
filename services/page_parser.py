import re

class PageParser:
    @staticmethod
    def parse(pages_str: str) -> list[int]:
        pages = set()
        for part in re.split(r',', pages_str):
            part = part.strip()
            if not part:
                continue
            if re.match(r'^\d+-\d+$', part):
                start, end = map(int, part.split('-'))
                if start > end:
                    raise ValueError("Rango inválido.")
                pages.update(range(start, end + 1))
            elif re.match(r'^\d+$', part):
                pages.add(int(part))
            else:
                raise ValueError(f"Formato inválido: '{part}'")
        return sorted(list(pages))
