import nbformat
import os
import sys
import re

def split_paragraphs(text):
    """
    Split a Markdown string into paragraphs.
    A paragraph is separated by one or more blank lines.
    """
    return re.split(r'\n\s*\n', text.strip())

def convert_doc_paragraphs_to_raw(nb_path):
    nb = nbformat.read(nb_path, as_version=4)
    new_cells = []
    changed = False
    for cell in nb.cells:
        if cell.cell_type == 'markdown' and ':doc:' in cell.source:
            changed = True
            paragraphs = split_paragraphs(cell.source)
            for para in paragraphs:
                if ':doc:' in para:
                    # Move the whole paragraph to a raw reStructuredText cell
                    raw_cell = nbformat.v4.new_raw_cell(para.strip())
                    raw_cell.metadata['raw_mimetype'] = 'text/restructuredtext'
                    new_cells.append(raw_cell)
                else:
                    # Keep paragraph as markdown
                    new_cells.append(nbformat.v4.new_markdown_cell(para.strip()))
        else:
            # Keep all other cells unchanged
            new_cells.append(cell)

    
    if changed :
        nb.cells = new_cells
        nbformat.write(nb, nb_path)
        print(f"✅ Made compatible with doc: {nb_path}")

def clean_outputs(nb_path):
    nb = nbformat.read(nb_path, as_version=4)
    changed = False

    for cell in nb.cells:
        if cell.cell_type == 'code' and 'outputs' in cell:
            new_outputs = []
            for output in cell.outputs:
                keep = False

                # Keep print() (stdout/stream)
                if output.output_type == 'stream' and output.name == 'stdout':
                    keep = True

                # Keep images (display_data or execute_result with MIME types)
                if output.output_type in ('display_data', 'execute_result'):
                    if 'image/png' in output.get('data', {}) or 'image/jpeg' in output.get('data', {}):
                        keep = True

                if keep:
                    new_outputs.append(output)
                else:
                    changed = True

            cell.outputs = new_outputs

            # deleted execution_count 
            if not new_outputs:
                cell.execution_count = None

    if changed:
        nbformat.write(nb, nb_path)
        print(f"✅ Cleaned: {nb_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python clean_outputs.py dossier_ou_fichiers.ipynb [...]")
        sys.exit(1)

    for path in sys.argv[1:]:
        if os.path.isfile(path) and path.endswith(".ipynb"):
            clean_outputs(path)
            convert_doc_paragraphs_to_raw(path)
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for f in files:
                    if f.endswith(".ipynb"):
                        clean_outputs(os.path.join(root, f))
                        convert_doc_paragraphs_to_raw(os.path.join(root, f))
