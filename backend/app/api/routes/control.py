from fastapi import APIRouter, HTTPException
from app.services.camera import Camera
from app.models.hsv import HSVUpdate
from app.models.shapes import SelectShapes, ShapeType
from app.utils.helpers import get_json_settings, set_json_settings
import json

router = APIRouter(prefix='/control')
cam = Camera()

@router.put("/update-hsv", tags=["control"])
async def update_hsv(hsv: HSVUpdate):
    try:
        # Crear los arrays lower y upper HSV
        lower_hsv = [hsv.lower_h, hsv.lower_s, hsv.lower_v]
        upper_hsv = [hsv.upper_h, hsv.upper_s, hsv.upper_v]

        # Establecer los valores HSV en la cámara
        cam.set_hsv(lower=lower_hsv, upper=upper_hsv)

        # Retornar la respuesta
        return {"status": "success", "lower_hsv": lower_hsv, "upper_hsv": upper_hsv}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/hsv", tags=["control"])
async def hsv():

    return {
        'lower_h': int(cam.hsv.lower_hsv[0]),
        'lower_s': int(cam.hsv.lower_hsv[1]),
        'lower_v': int(cam.hsv.lower_hsv[2]),
        'upper_h': int(cam.hsv.upper_hsv[0]),
        'upper_s': int(cam.hsv.upper_hsv[1]),
        'upper_v': int(cam.hsv.upper_hsv[2]),
    }

@router.post("/reset-hsv", tags=["control"])
async def reset_hsv():
    cam.reset_hsv()
    config = get_json_settings()

    lower_hsv = config['lower_hsv']
    upper_hsv = config['upper_hsv']

    cam.set_hsv(lower=lower_hsv, upper=upper_hsv)

    return {"status": "success"}

@router.post("/set-hsv", tags=["control"])
async def set_hsv(hsv: HSVUpdate):
    lower_hsv = [hsv.lower_h, hsv.lower_s, hsv.lower_v]
    upper_hsv = [hsv.upper_h, hsv.upper_s, hsv.upper_v]

    config = get_json_settings()

    config['lower_hsv'] = lower_hsv
    config['upper_hsv'] = upper_hsv 

    cam.set_hsv(lower=lower_hsv, upper=upper_hsv)

    set_json_settings(config)

    return {"status": "success", "lower_hsv": lower_hsv, "upper_hsv": upper_hsv}   

@router.put("/update-shape", tags=["control"])
async def update_shape(shape: SelectShapes):
    try:
        config = get_json_settings()
        
        if shape == SelectShapes.CIRCLE:
            cam.set_shape(ShapeType.CIRCLE.value)
        elif shape == SelectShapes.QUADRILATERAL:
            cam.set_shape(ShapeType.QUADRILATERAL.value)
        elif shape == SelectShapes.TRIANGLE:
            cam.set_shape(ShapeType.TRIANGLE.value)
        else: 
            raise HTTPException(status_code=400, detail="Invalid shape selection")
            
        config['target_shape'] = str(cam.target_shape)

        set_json_settings(config)
            
        return {"status": "success", "shape": str(cam.target_shape)}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e)) 
