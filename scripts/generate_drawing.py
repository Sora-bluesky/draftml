# generate_drawing.py - Single part drawing generator for FreeCAD
# Runs inside FreeCAD Python environment via execute_python
# ASCII-only (cp932 constraint)

import FreeCAD
import Part
import os


def generate_drawing(part_no, width, height, length, thickness,
                     lip_height=20.0, output_dir="output"):
    """Generate a manufacturing drawing for a C-channel steel part.

    Args:
        part_no: Part number string (e.g. "C-100-50-20-32")
        width: Flange width in mm
        height: Web height in mm
        length: Part length in mm
        thickness: Plate thickness in mm
        lip_height: Lip height in mm (default 20)
        output_dir: Output directory path

    Returns:
        dict with status, part_no, checks, and file paths
    """
    result = {
        "status": "ok",
        "part_no": part_no,
        "checks": {},
        "files": {},
        "error": None,
    }

    doc = None
    try:
        # Sanitize document name (no hyphens allowed)
        doc_name = part_no.replace("-", "_")

        # Close any existing document with same name
        if doc_name in FreeCAD.listDocuments():
            FreeCAD.closeDocument(doc_name)

        # 1. Create document
        doc = FreeCAD.newDocument(doc_name)

        # 2. Create C-channel 3D model using Part API
        t = float(thickness)
        H = float(height)
        W = float(width)
        Lp = float(lip_height)
        L = float(length)

        # Validate parameters
        if any(v <= 0 for v in [t, H, W, Lp, L]):
            raise ValueError("All dimensions must be > 0")
        if t >= W / 2 or t >= H / 2:
            raise ValueError("Thickness too large for given dimensions")
        if Lp <= t:
            raise ValueError("Lip height must be > thickness")

        # 12-point closed wire for C-channel cross-section
        points = [
            FreeCAD.Vector(0, 0, 0),
            FreeCAD.Vector(0, H, 0),
            FreeCAD.Vector(W, H, 0),
            FreeCAD.Vector(W, H - Lp, 0),
            FreeCAD.Vector(W - t, H - Lp, 0),
            FreeCAD.Vector(W - t, H - t, 0),
            FreeCAD.Vector(t, H - t, 0),
            FreeCAD.Vector(t, t, 0),
            FreeCAD.Vector(W - t, t, 0),
            FreeCAD.Vector(W - t, Lp, 0),
            FreeCAD.Vector(W, Lp, 0),
            FreeCAD.Vector(W, 0, 0),
            FreeCAD.Vector(0, 0, 0),  # close
        ]

        wire = Part.makePolygon(points)
        face = Part.Face(wire)
        solid = face.extrude(FreeCAD.Vector(0, 0, L))

        obj = doc.addObject("Part::Feature", "CChannel")
        obj.Shape = solid
        doc.recompute()

        # Quality check: shape
        bb = obj.Shape.BoundBox
        result["checks"]["valid"] = obj.Shape.isValid()
        result["checks"]["bb_x"] = abs(bb.XLength - W) < 0.1
        result["checks"]["bb_y"] = abs(bb.YLength - H) < 0.1
        result["checks"]["bb_z"] = abs(bb.ZLength - L) < 0.1

        exp_area = H * t + 2 * (W - t) * t + 2 * (Lp - t) * t
        exp_vol = exp_area * L
        vol_err = abs(obj.Shape.Volume - exp_vol) / exp_vol if exp_vol > 0 else 1
        result["checks"]["volume_ok"] = vol_err < 0.01

        # 3. TechDraw page + views
        template_dir = FreeCAD.getResourceDir() + "Mod/TechDraw/Templates/"
        template_file = template_dir + "A3_Landscape_ISO5457_minimal.svg"

        page = doc.addObject("TechDraw::DrawPage", "Page")
        tmpl = doc.addObject("TechDraw::DrawSVGTemplate", "Template")
        tmpl.Template = template_file
        page.Template = tmpl
        doc.recompute()

        # Populate title block fields (ISO 5457 field names)
        fields = tmpl.EditableTexts
        if "identification_number" in fields:
            fields["identification_number"] = part_no
        if "title" in fields:
            fields["title"] = "C-Channel {}".format(part_no)
        if "document_type" in fields:
            fields["document_type"] = "Manufacturing Drawing"
        tmpl.EditableTexts = fields
        doc.recompute()

        # Determine scale based on length
        if L > 2000:
            long_scale = 0.1  # 1:10
        elif L > 500:
            long_scale = 0.2  # 1:5
        else:
            long_scale = 0.5  # 1:2

        # Front View
        front = doc.addObject("TechDraw::DrawViewPart", "FrontView")
        front.Source = [obj]
        front.Direction = FreeCAD.Vector(0, -1, 0)
        front.XDirection = FreeCAD.Vector(1, 0, 0)
        page.addView(front)
        doc.recompute()
        front.ScaleType = u"Custom"
        front.Scale = long_scale
        front.X = 210.0
        front.Y = 230.0
        doc.recompute()

        # Top View
        top = doc.addObject("TechDraw::DrawViewPart", "TopView")
        top.Source = [obj]
        top.Direction = FreeCAD.Vector(0, 0, -1)
        top.XDirection = FreeCAD.Vector(1, 0, 0)
        page.addView(top)
        doc.recompute()
        top.ScaleType = u"Custom"
        top.Scale = long_scale
        top.X = 210.0
        top.Y = 195.0
        doc.recompute()

        # Right View (side)
        right = doc.addObject("TechDraw::DrawViewPart", "RightView")
        right.Source = [obj]
        right.Direction = FreeCAD.Vector(1, 0, 0)
        right.XDirection = FreeCAD.Vector(0, 1, 0)
        page.addView(right)
        doc.recompute()
        right.ScaleType = u"Custom"
        right.Scale = long_scale
        right.X = 60.0
        right.Y = 150.0
        doc.recompute()

        # End View (cross-section at 1:1)
        end = doc.addObject("TechDraw::DrawViewPart", "EndView")
        end.Source = [obj]
        end.Direction = FreeCAD.Vector(0, 0, 1)
        end.XDirection = FreeCAD.Vector(1, 0, 0)
        page.addView(end)
        doc.recompute()
        end.ScaleType = u"Custom"
        end.Scale = 1.0
        end.X = 280.0
        end.Y = 80.0
        doc.recompute()

        # 4. Dimensions on EndView
        # Force GUI update so TechDraw computes view geometry
        import time
        try:
            import FreeCADGui
            doc.recompute()
            FreeCADGui.updateGui()
            time.sleep(0.3)
            doc.recompute()
            FreeCADGui.updateGui()
        except ImportError:
            doc.recompute()
            time.sleep(1.0)
            doc.recompute()

        # Enumerate vertices to find correct references
        vertex_map = {}
        for i in range(20):
            try:
                v = end.getVertexByIndex(i)
                if v:
                    vertex_map[i] = (round(v.Point.x, 1), round(v.Point.y, 1))
            except Exception:
                break

        # Find vertices for dimensions based on coordinates
        half_w = W / 2.0
        half_h = H / 2.0

        def find_vertex(target_x, target_y, tol=1.0):
            for idx, (vx, vy) in vertex_map.items():
                if abs(vx - target_x) < tol and abs(vy - target_y) < tol:
                    return idx
            return None

        # Web height: left-bottom to left-top
        v_bl = find_vertex(-half_w, -half_h)
        v_tl = find_vertex(-half_w, half_h)

        # Flange width: bottom-left to bottom-right
        v_br = find_vertex(half_w, -half_h)

        # Lip: right-bottom to right-lip
        lip_y = -half_h + Lp
        v_lip = find_vertex(half_w, lip_y)

        # Thickness: lip outer to lip inner
        v_lip_inner = find_vertex(half_w - t, lip_y)

        dims_added = 0

        if v_bl is not None and v_tl is not None:
            dim = doc.addObject("TechDraw::DrawViewDimension", "DimWebH")
            dim.Type = "DistanceY"
            dim.References2D = [(end, "Vertex{}".format(v_bl)),
                                (end, "Vertex{}".format(v_tl))]
            dim.FormatSpec = "%.0f"
            dim.X = -40.0
            page.addView(dim)
            dims_added += 1

        if v_bl is not None and v_br is not None:
            dim = doc.addObject("TechDraw::DrawViewDimension", "DimFlangeW")
            dim.Type = "DistanceX"
            dim.References2D = [(end, "Vertex{}".format(v_bl)),
                                (end, "Vertex{}".format(v_br))]
            dim.FormatSpec = "%.0f"
            dim.Y = 30.0
            page.addView(dim)
            dims_added += 1

        if v_br is not None and v_lip is not None:
            dim = doc.addObject("TechDraw::DrawViewDimension", "DimLipH")
            dim.Type = "DistanceY"
            dim.References2D = [(end, "Vertex{}".format(v_br)),
                                (end, "Vertex{}".format(v_lip))]
            dim.FormatSpec = "%.0f"
            dim.X = 30.0
            page.addView(dim)
            dims_added += 1

        if v_lip is not None and v_lip_inner is not None:
            dim = doc.addObject("TechDraw::DrawViewDimension", "DimThick")
            dim.Type = "DistanceX"
            dim.References2D = [(end, "Vertex{}".format(v_lip)),
                                (end, "Vertex{}".format(v_lip_inner))]
            dim.FormatSpec = "%.1f"
            dim.X = 40.0
            dim.Y = -10.0
            page.addView(dim)
            dims_added += 1

        # Length dimension on RightView
        rv_verts = {}
        for i in range(20):
            try:
                v = right.getVertexByIndex(i)
                if v:
                    rv_verts[i] = (round(v.Point.x, 1), round(v.Point.y, 1))
            except Exception:
                break

        if len(rv_verts) >= 2:
            # Find two vertices with max Y distance
            sorted_by_y = sorted(rv_verts.items(), key=lambda kv: kv[1][1])
            v_bottom = sorted_by_y[0][0]
            v_top = sorted_by_y[-1][0]
            dim = doc.addObject("TechDraw::DrawViewDimension", "DimLen")
            dim.Type = "DistanceY"
            dim.References2D = [(right, "Vertex{}".format(v_bottom)),
                                (right, "Vertex{}".format(v_top))]
            dim.FormatSpec = "%.0f"
            dim.X = -20.0
            page.addView(dim)
            dims_added += 1

        result["checks"]["dims"] = dims_added
        doc.recompute()

        # 5. Export PDF and DXF
        # GUI update required for template background rendering in PDF
        import TechDrawGui
        import TechDraw as TD
        doc.recompute()
        FreeCADGui.updateGui()
        time.sleep(0.5)
        doc.recompute()
        FreeCADGui.updateGui()

        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)

        pdf_path = os.path.join(output_dir, "{}.pdf".format(part_no))
        dxf_path = os.path.join(output_dir, "{}.dxf".format(part_no))

        TechDrawGui.exportPageAsPdf(page, pdf_path)
        TD.writeDXFPage(page, dxf_path)

        result["files"]["pdf"] = pdf_path
        result["files"]["dxf"] = dxf_path
        result["checks"]["pdf_exists"] = os.path.exists(pdf_path)
        result["checks"]["dxf_exists"] = os.path.exists(dxf_path)

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    finally:
        # Close document to free memory
        if doc and doc.Name in FreeCAD.listDocuments():
            FreeCAD.closeDocument(doc.Name)

    return result
