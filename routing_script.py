# Author - Nikita

import adsk.core, adsk.fusion, traceback
import math, json
selected_faces_tokens = {}
pipeRadius = 0.01
pipeThickness = '0.2mm'
points = []
selected_face1 = 0
selected_face2 = 0
def run(context):
    ui = None
    try: 
        app = adsk.core.Application.get()
        ui = app.userInterface

        global pipeRadius
        # doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = app.activeProduct
        
        # Get the root component of the active design.
        rootComp = design.rootComponent
        feats = rootComp.features
        # Create a new sketch on the xy plane.
        sketch = rootComp.sketches.add(rootComp.xYConstructionPlane)
        save_and_load_connected_faces()
        Nstart,end = select_and_create_normal_vector_lines(0.05, sketch)
        # set recursion function to find all the intersection points.
        points = []
        ####### section different start points#####
        tolerance = pipeRadius
        x,y,z = Nstart.x,Nstart.y,Nstart.z
        point1 = adsk.core.Point3D.create(x + tolerance, y, z)
        point2 = adsk.core.Point3D.create(x - tolerance, y, z)
        point3 = adsk.core.Point3D.create(x, y + tolerance, z)
        point4 = adsk.core.Point3D.create(x, y - tolerance, z)
        point5 = adsk.core.Point3D.create(x, y, z + tolerance)
        point6 = adsk.core.Point3D.create(x, y, z - tolerance)

        Spoints = [point1, point2, point3, point4, point5, point6]
        
        
        
        
        P = []
        ###### end section#########
        for start in Spoints:

            temp = check_intersection_2_points(start, end,sketch,rootComp,[])
            temp = [point for i,point in enumerate(temp) if point not in temp[:i]]
            if len(temp) >= len(P):
                P=[]
                P.extend(temp)
                P[0] = Nstart
                
            else:
                continue

        if not P:
            P = []
            P.append(Nstart)
            P.append(end)   

        # while sketch.sketchCurves:
        #     sketch.sketchCurves[0].deleteMe()
        create_spline(P,sketch)
        # create_non_intersecting_spline(start, end, sketch)
        piping(sketch,pipeRadius = 0.02)
        print("hi")
        
       
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def save_face_token(face, body):
    global selected_faces_tokens
    if face:
        face_token = face.entity.entityToken
        if not face_token in selected_faces_tokens:
            selected_faces_tokens[face_token]=False
    if body:
        for faces in selected_faces_tokens:
            if not selected_faces_tokens[faces]:
                selected_faces_tokens[faces] = body.entityToken

def select_and_create_normal_vector_lines(distance, sketch):
    try:
        # Get the active design and user interface
        app = adsk.core.Application.get()
        design = app.activeProduct
        root_comp = design.rootComponent
        ui = app.userInterface
        global selected_face1
        global selected_face2
        
        # Create a new sketch
        # sketch = root_comp.sketches.add(root_comp.xYConstructionPlane)

        # Select the first face
        selected_face1 = ui.selectEntity("Select first face", "Faces")
        center_point1 = adsk.core.Point3D.create(selected_face1.entity.centroid.x, selected_face1.entity.centroid.y, selected_face1.entity.centroid.z)
        save_face_token(selected_face1, 0)
        # Select the second face
        selected_face2 = ui.selectEntity("Select second face", "Faces")
        center_point2 = adsk.core.Point3D.create(selected_face2.entity.centroid.x, selected_face2.entity.centroid.y, selected_face2.entity.centroid.z)
        save_face_token(selected_face2, 0)
        # Create the normal vector lines
        
        normal1 = selected_face1.entity.geometry.normal
        if selected_face1.entity.isParamReversed:
            normal1.scaleBy(-1)
        end_point1 = adsk.core.Point3D.create(center_point1.x + normal1.x*distance, center_point1.y + normal1.y*distance, center_point1.z + normal1.z*distance)
        sketch.sketchCurves.sketchLines.addByTwoPoints(center_point1, end_point1)

        normal2 = selected_face2.entity.geometry.normal
        if selected_face2.entity.isParamReversed:
            normal2.scaleBy(-1)
        end_point2 = adsk.core.Point3D.create(center_point2.x + normal2.x*distance, center_point2.y + normal2.y*distance, center_point2.z + normal2.z*distance)
        sketch.sketchCurves.sketchLines.addByTwoPoints(center_point2, end_point2)

        return end_point1, end_point2
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
def check_intersection_2_points(start, end, sketch, rootComp, points):
    centerpoint = 0
    lines =[]
    global pipeRadius
    ######### create points around start point #########
    

    ############ end section ##############################
    
    line = sketch.sketchCurves.sketchLines.addByTwoPoints(start, end)
    
    # i have to check also the bodies out of occurances.
    for Occurrences in rootComp.allOccurrences:
        for body in Occurrences.bRepBodies:
            if body.entityToken in selected_faces_tokens.values():
                continue
            for face in body.faces :
                if face.entityToken in selected_faces_tokens:
                    continue
                res: adsk.core.ObjectCollection = line.geometry.intersectWithSurface(face.geometry)
                if res.count > 0: 
                    if face.boundingBox.contains(res[0]):
                        BBpo = {}
                        for edge in face.edges:
                            BBpo[edge.startVertex.geometry.distanceTo(res[0])] = edge.startVertex.geometry
                            BBpo[edge.endVertex.geometry.distanceTo(res[0])] = edge.endVertex.geometry
                            BBpo[edge.pointOnEdge.distanceTo(res[0])] = edge.pointOnEdge
                        res[0].translateBy(adsk.core.Vector3D.create(0,0,0.1))
                        centerpoint = res[0]
                        
                if centerpoint:
                    break 
            if centerpoint:
                break 
        if centerpoint:
            break 
    for body in rootComp.bRepBodies:
        
        if selected_face1.entity.entityToken in selected_faces_tokens:
            if body.entityToken == selected_faces_tokens[selected_face1.entity.entityToken]:
                continue
        if selected_face2.entity.entityToken in selected_faces_tokens:
            if body.entityToken == selected_faces_tokens[selected_face2.entity.entityToken]:
                continue
            
        for face in body.faces:
            res: adsk.core.ObjectCollection = line.geometry.intersectWithSurface(face.geometry)
            if res.count > 0: 

                if face.boundingBox.contains(res[0]):
                    if face.entityToken in selected_faces_tokens:
                        continue
                    
                    centerpoint = res[0].copy()
                    res[0].translateBy(adsk.core.Vector3D.create(0,0,0.1))
                    
            if centerpoint:
                break 
        if centerpoint:
            break     
         
    if centerpoint:
        line.deleteMe()

        points.extend(check_intersection_2_points(start, res[0] ,sketch, rootComp, points))
        points.extend(check_intersection_2_points(res[0], end ,sketch, rootComp, points))
        return points
    else:
        line.deleteMe()
        points.append(start)
        points.append( end)
        return points
def create_spline(points,sketch):
    
    
    
    objCol = adsk.core.ObjectCollection.create()
    for point in points:
        objCol.add(point)
    
    sketch.sketchCurves.sketchFittedSplines.add(objCol)
def save_and_load_connected_faces():
    global selected_faces_tokens
    try:
        if selected_faces_tokens:
            with open('C:\\Users\RybalkaNikita\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\Scripts\chatGPT - path creation\paths.txt', 'w') as f:
                json.dump(selected_faces_tokens, f)
        else:
            with open('C:\\Users\RybalkaNikita\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\Scripts\chatGPT - path creation\paths.txt', 'r') as f:
                selected_faces_tokens = json.load(f)   
    except:
        with open('C:\\Users\RybalkaNikita\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\Scripts\chatGPT - path creation\paths.txt', 'w') as f:
            json.dump(selected_faces_tokens, f)

def create_non_intersecting_spline(start_point, end_point,sketch):
    try:
        # Get the active design and user interface
        app = adsk.core.Application.get()
        design = app.activeProduct
        ui = app.userInterface

        # Create a temporary sketch
        # sketch = design.sketches.add(design.rootComponent.xYConstructionPlane)

        # Create a temporary spline line between the starting point and end point
        objCol = adsk.core.ObjectCollection.create()
        objCol.add(start_point)
        objCol.add(end_point)
        temp_spline = sketch.sketchCurves.sketchFittedSplines.add(objCol)
        intersection_point = None
        # Iterate through all bodies in the design
        for Occurrences in design.rootComponent.allOccurrences:
            for body in Occurrences.bRepBodies:
                # Check for intersection with the temporary spline line
                for edge in body.edges:
                    start_point = edge.startVertex.geometry
                    end_point = edge.endVertex.geometry
                    for spline_point in temp_spline.geometry.controlPoints:
                        # check if the point is on the edge by comparing the distance between the point and the edge with a small tolerance
                        tolerance = 0.01  # you can adjust the tolerance as needed
                        if (spline_point.distanceTo(start_point) + spline_point.distanceTo(end_point) - start_point.distanceTo(end_point)) < tolerance:
                            intersection_point = spline_point
                            break
                    if intersection_point:
                        break
                
                # intersections = body.intersectWithCurve(temp_spline)

                # If an intersection is found
                if intersection_point:
                    # Divide the temporary spline line into two parts at the intersection point
                    
                    temp, new_spline = temp_spline.split(intersection_point)

                    # Move the intersection point by a small amount in the direction of the normal of the intersecting face
                    new_intersection_point = intersection_point.copy()
                    IV=intersection_point.asVector()
                    IV.normalize()
                    IV.scaleBy(0.01)
                    new_intersection_point.translateBy(IV)
    # Create a new temporary spline line between the starting point and the new intersection point
                    obj = adsk.core.ObjectCollection.create()
                    obj.add(start_point)
                    obj.add(new_intersection_point)
                    temp_spline = sketch.sketchCurves.sketchFittedSplines.add(obj)

        # Return the final spline line
        return temp_spline
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def piping(sketch,pipeRadius = 0.02):
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        
        selObj = sketch.sketchCurves

        comp = design.rootComponent
        
        # create path
        feats = comp.features
        chainedOption = adsk.fusion.ChainedCurveOptions.connectedChainedCurves
        if adsk.fusion.BRepEdge.cast(selObj[0]):
            chainedOption = adsk.fusion.ChainedCurveOptions.tangentChainedCurves
        # path = adsk.fusion.Path.create(selObj.sketchLines[0], chainedOption)
        # Create a PathGeometry object from the list of sketch lines
        path_geometry = adsk.core.ObjectCollection.create()
        for line_index in range(len(selObj)):
            if line_index==1:
                continue
            path_geometry.add(selObj[line_index])
        path_geometry.add(selObj[1])
        path = feats.createPath(path_geometry)

        # create profile
        planes = comp.constructionPlanes
        planeInput = planes.createInput()
        planeInput.setByDistanceOnPath(selObj[0], adsk.core.ValueInput.createByReal(0))
        plane = planes.add(planeInput)
        
        sketches = comp.sketches
        sketch = sketches.add(plane)
        
        center = plane.geometry.origin
        center = sketch.modelToSketchSpace(center)
        sketch.sketchCurves.sketchCircles.addByCenterRadius(center, pipeRadius)
        profile = sketch.profiles[0]
        
        # create sweep
        sweepFeats = feats.sweepFeatures
        sweepInput = sweepFeats.createInput(profile, path, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        sweepInput.orientation = adsk.fusion.SweepOrientationTypes.PerpendicularOrientationType
        sweepFeat = sweepFeats.add(sweepInput)

        
        objCol = adsk.core.ObjectCollection.create()

        
        if objCol.count == 0:
            bodies = sweepFeat.bodies
            for body in bodies:
                objCol.add(body)
        

        save_face_token(0, body)
        save_and_load_connected_faces()
        app.activeViewport.refresh()

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))       
