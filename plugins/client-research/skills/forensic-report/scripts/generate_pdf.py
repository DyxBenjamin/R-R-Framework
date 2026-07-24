#!/usr/bin/env python3
"""Genera report.pdf a partir del report.json unificado de client-research.

Usa unicamente la libreria estandar de Python -- sin dependencias de
terceros -- para evitar el problema de dependencias sin gestionar que ya
existe en este repo (ver skill-creator/scripts/*.py, que asume PyYAML
preinstalado sin ningun mecanismo de instalacion). Ver
.agents/kt/plans/client-research-reporting.md para el porque de esta
decision.

Uso:
    python3 generate_pdf.py <report.json> <salida.pdf>
"""
import json
import sys

PAGE_WIDTH = 612  # US Letter, en puntos
PAGE_HEIGHT = 792
MARGIN = 50
LINE_HEIGHT = 16
FONT_BODY = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
FONT_SIZE_BODY = 10
FONT_SIZE_H1 = 18
FONT_SIZE_H2 = 13


def escape_pdf_text(value):
    """Escapa texto para la forma de string literal de PDF.

    Obligatorio antes de insertar CUALQUIER texto de terceros (findings,
    URLs, nombres) en el content stream -- no solo por correccion sintactica,
    sino para que texto abierto de la web nunca pueda romper la cadena o
    inyectar operadores PDF fuera de ella.
    """
    if value is None:
        return ""
    text = str(value)
    text = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    text = text.replace("\r", " ").replace("\n", " ")
    # El string literal simple de PDF usa PDFDocEncoding/Latin-1; cualquier
    # caracter fuera de ese rango se reemplaza en vez de emitir bytes que
    # corromperian el stream.
    text = text.encode("latin-1", "replace").decode("latin-1")
    return text


class MinimalPDF:
    """Escritor de PDF minimo, sin dependencias de terceros.

    Soporta texto simple (las dos fuentes base14 Helvetica/Helvetica-Bold,
    que no requieren embeberse), paginacion automatica, y una linea
    horizontal de separador -- lo justo para un reporte forense legible.
    """

    def __init__(self):
        self.pages = []  # lista de listas de operadores de contenido (bytes)
        self._new_page()

    def _new_page(self):
        self.pages.append([])
        self.y = PAGE_HEIGHT - MARGIN

    def _ensure_space(self, needed=LINE_HEIGHT):
        if self.y - needed < MARGIN:
            self._new_page()

    def text(self, value, size=FONT_SIZE_BODY, font=FONT_BODY, indent=0):
        self._ensure_space()
        safe = escape_pdf_text(value)
        font_ref = "/F1" if font == FONT_BODY else "/F2"
        op = "BT {0} {1} Tf {2} {3} Td ({4}) Tj ET\n".format(
            font_ref, size, MARGIN + indent, self.y, safe
        )
        self.pages[-1].append(op.encode("latin-1"))
        self.y -= max(size + 4, LINE_HEIGHT)

    def rule(self):
        self._ensure_space(8)
        op = "{0} {1} m {2} {1} l S\n".format(MARGIN, self.y, PAGE_WIDTH - MARGIN)
        self.pages[-1].append(op.encode("latin-1"))
        self.y -= 12

    def spacer(self, height=8):
        self.y -= height

    def save(self, path):
        objects = []  # objects[i-1] es el objeto indirecto numero i

        def add_object(body):
            objects.append(body)
            return len(objects)

        font_body_num = add_object(
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"
        )
        font_bold_num = add_object(
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>"
        )

        # Reservar el numero de objeto de /Pages antes de escribir las
        # paginas (cada una necesita referenciarlo como /Parent).
        pages_obj_num = len(objects) + 1
        objects.append(None)

        page_obj_nums = []
        for content_ops in self.pages:
            stream_bytes = b"".join(content_ops)
            content_obj_num = add_object(
                b"<< /Length "
                + str(len(stream_bytes)).encode("ascii")
                + b" >>\nstream\n"
                + stream_bytes
                + b"\nendstream"
            )
            page_body = (
                "<< /Type /Page /Parent {0} 0 R "
                "/Resources << /Font << /F1 {1} 0 R /F2 {2} 0 R >> >> "
                "/MediaBox [0 0 {3} {4}] /Contents {5} 0 R >>"
            ).format(
                pages_obj_num,
                font_body_num,
                font_bold_num,
                PAGE_WIDTH,
                PAGE_HEIGHT,
                content_obj_num,
            ).encode("ascii")
            page_obj_nums.append(add_object(page_body))

        kids = " ".join("{0} 0 R".format(n) for n in page_obj_nums)
        objects[pages_obj_num - 1] = (
            "<< /Type /Pages /Kids [{0}] /Count {1} >>".format(
                kids, len(page_obj_nums)
            ).encode("ascii")
        )

        catalog_num = add_object(
            "<< /Type /Catalog /Pages {0} 0 R >>".format(pages_obj_num).encode(
                "ascii"
            )
        )

        out = bytearray()
        out += b"%PDF-1.4\n"
        offsets = [0] * (len(objects) + 1)
        for i, body in enumerate(objects, start=1):
            offsets[i] = len(out)
            out += "{0} 0 obj\n".format(i).encode("ascii")
            out += body
            out += b"\nendobj\n"

        xref_offset = len(out)
        out += "xref\n0 {0}\n".format(len(objects) + 1).encode("ascii")
        out += b"0000000000 65535 f \n"
        for i in range(1, len(objects) + 1):
            out += "{0:010d} 00000 n \n".format(offsets[i]).encode("ascii")

        out += b"trailer\n"
        out += "<< /Size {0} /Root {1} 0 R >>\n".format(
            len(objects) + 1, catalog_num
        ).encode("ascii")
        out += b"startxref\n"
        out += "{0}\n".format(xref_offset).encode("ascii")
        out += b"%%EOF"

        with open(path, "wb") as f:
            f.write(bytes(out))


def render_report(report):
    pdf = MinimalPDF()
    pdf.text(
        "Reporte forense de investigacion -- {0}".format(report.get("client", "")),
        size=FONT_SIZE_H1,
        font=FONT_BOLD,
    )
    pdf.text("Generado: {0}".format(report.get("generated_at", "")), size=9)
    pdf.spacer(10)
    pdf.rule()
    pdf.spacer(6)

    sections = [
        ("stack_research", "Stack tecnologico", "aggregate_stack"),
        ("vendor_research", "Proveedores actuales", "aggregate"),
        ("competitor_research", "Competidores/partners con evidencia", "aggregate"),
    ]
    sources = report.get("sources", {})
    for key, title, agg_key in sections:
        data = sources.get(key) or {}
        pdf.text(title, size=FONT_SIZE_H2, font=FONT_BOLD)
        pdf.spacer(4)
        agg = data.get(agg_key) or {}
        wrote_any = False
        for category, values in agg.items():
            if not values:
                continue
            wrote_any = True
            for v in values:
                if isinstance(v, dict):
                    name = v.get("name", "")
                    mentions = v.get("mentions")
                    suffix = (
                        " ({0} fuente{1})".format(
                            mentions, "s" if mentions != 1 else ""
                        )
                        if mentions is not None
                        else ""
                    )
                    pdf.text("- {0}{1}".format(name, suffix), indent=10)
                else:
                    pdf.text("- {0}".format(v), indent=10)
        if not wrote_any:
            pdf.text("Sin hallazgos.", indent=10)
        pdf.spacer(10)

    cross_refs = report.get("cross_references", [])
    if cross_refs:
        pdf.text("Referencias cruzadas", size=FONT_SIZE_H2, font=FONT_BOLD)
        pdf.spacer(4)
        for ref in cross_refs:
            appears_in = ", ".join(ref.get("appears_in", []))
            pdf.text(
                "- {0}: aparece en {1}".format(ref.get("name", ""), appears_in),
                indent=10,
            )
            if ref.get("detail"):
                pdf.text(ref["detail"], indent=20, size=9)
        pdf.spacer(10)

    summary = report.get("verification_summary", {})
    if summary:
        pdf.text("Verificacion de fuentes", size=FONT_SIZE_H2, font=FONT_BOLD)
        pdf.spacer(4)
        pdf.text(
            "Total de fuentes verificadas: {0}".format(
                summary.get("total_sources", 0)
            ),
            indent=10,
        )
        for stype, count in (summary.get("source_types_breakdown") or {}).items():
            pdf.text("- {0}: {1}".format(stype, count), indent=20)

    return pdf


def main():
    if len(sys.argv) != 3:
        print("Uso: python3 generate_pdf.py <report.json> <salida.pdf>", file=sys.stderr)
        sys.exit(1)
    report_path, out_path = sys.argv[1], sys.argv[2]
    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)
    pdf = render_report(report)
    pdf.save(out_path)
    print("PDF generado: {0}".format(out_path))


if __name__ == "__main__":
    main()
