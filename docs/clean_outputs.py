import nbformat
import os
import sys

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
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for f in files:
                    if f.endswith(".ipynb"):
                        clean_outputs(os.path.join(root, f))
