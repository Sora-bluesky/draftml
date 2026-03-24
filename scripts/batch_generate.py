# batch_generate.py - CSV batch drawing generation pipeline for FreeCAD
# Runs inside FreeCAD Python environment via execute_python
# ASCII-only (cp932 constraint)

import csv
import os
import sys
import time


def main(csv_path, output_dir):
    """Read products.csv and generate drawings for each part.

    Args:
        csv_path: Path to products.csv
        output_dir: Output directory for PDF/DXF files

    Returns:
        dict with summary statistics
    """
    # Import generate_drawing from same directory
    # __file__ may not exist in FreeCAD execute_python context
    csv_dir = os.path.dirname(os.path.abspath(csv_path))
    script_dir = os.path.join(csv_dir, "scripts")
    if os.path.isdir(script_dir) and script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    from generate_drawing import generate_drawing

    if not os.path.exists(csv_path):
        return {"error": "CSV not found: {}".format(csv_path)}

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    # Read CSV
    products = []
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            products.append(row)

    total = len(products)
    success = 0
    failed = 0
    results = []
    start_time = time.time()

    print("=" * 50)
    print("Batch Drawing Generation")
    print("Products: {}".format(total))
    print("Output: {}".format(output_dir))
    print("=" * 50)

    for i, prod in enumerate(products):
        part_no = prod.get("part_no", "UNKNOWN")
        print("\n[{}/{}] Processing: {}".format(i + 1, total, part_no))

        try:
            width = float(prod.get("width", 0))
            height = float(prod.get("height", 0))
            length = float(prod.get("length", 0))
            thickness = float(prod.get("thickness", 0))
            hole_diam = float(prod.get("hole_diam", 0))

            result = generate_drawing(
                part_no=part_no,
                width=width,
                height=height,
                length=length,
                thickness=thickness,
                lip_height=20.0,  # default lip height
                output_dir=output_dir,
            )

            results.append(result)

            if result["status"] == "ok":
                success += 1
                checks = result.get("checks", {})
                all_ok = all(v for k, v in checks.items()
                            if isinstance(v, bool))
                status_str = "OK" if all_ok else "WARN"
                print("  -> {} (dims={})".format(
                    status_str, checks.get("dims", 0)))
            else:
                failed += 1
                print("  -> ERROR: {}".format(result.get("error", "unknown")))

        except Exception as e:
            failed += 1
            results.append({
                "status": "error",
                "part_no": part_no,
                "error": str(e),
            })
            print("  -> EXCEPTION: {}".format(str(e)))

    elapsed = time.time() - start_time

    # Summary
    summary = {
        "total": total,
        "success": success,
        "failed": failed,
        "elapsed_sec": round(elapsed, 1),
        "results": results,
    }

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("  Total:   {}".format(total))
    print("  Success: {}".format(success))
    print("  Failed:  {}".format(failed))
    print("  Time:    {:.1f}s".format(elapsed))
    print("=" * 50)

    # Write summary to file
    summary_path = os.path.join(output_dir, "batch_summary.txt")
    with open(summary_path, "w") as f:
        f.write("Batch Generation Summary\n")
        f.write("Date: {}\n".format(time.strftime("%Y-%m-%d %H:%M:%S")))
        f.write("CSV: {}\n".format(csv_path))
        f.write("Total: {}, Success: {}, Failed: {}\n".format(
            total, success, failed))
        f.write("Time: {:.1f}s\n\n".format(elapsed))
        for r in results:
            pno = r.get("part_no", "?")
            st = r.get("status", "?")
            err = r.get("error", "")
            checks = r.get("checks", {})
            f.write("{}: {} {}\n".format(pno, st, err))
            if checks:
                for k, v in checks.items():
                    f.write("  {}={}\n".format(k, v))

    return summary


if __name__ == "__main__":
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "products.csv"
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
    main(csv_path, out_dir)
