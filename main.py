import os
import sys
from typing import Union

from sanic import Sanic, SanicException
from sanic.request import Request
from sanic.response import file, JSONResponse

from static.utils import Model, Processor

STATIC_PATH: str = "static"
models: list = []

app = Sanic("BG-Remove-API")
app.static("static", "static")

if not os.path.exists("TEMP"):
    os.makedirs("TEMP")


@app.route("/", methods=["GET"])
async def root(request: Request) -> JSONResponse:
    return JSONResponse(
        body={
            "statusText" : "Root Endpoint of BG-Remove-API",
        },
        status=200,
    )


@app.route("/clean", methods=["GET"])
async def clean(request: Request) -> JSONResponse:
    """
    BASH

        curl -X GET "http://localhost:9090/clean" -s
    
    """

    if len(os.listdir("TEMP")) == 0:
        return JSONResponse(
            body={
                "statusText" : "Temp Directory is already Clean",
            },
            status=200,
        )

    for filename in os.listdir("TEMP"):
        os.remove(f"TEMP/{filename}")
     
    return JSONResponse(
        body={
            "statusText" : "Cleaned Temp Directory",
        },
        status=200,
    )


@app.route("/<infer_type:str>", methods=["GET", "POST"])
async def processing(request: Request, infer_type: str) -> JSONResponse:
    """
    BASH

        curl -X POST -L "http://localhost:9090/remove?rtype=json" -F file=@"/<PATH>/img1.png" -o "<PATH>/temp.json"
        curl -X POST -L "http://localhost:9090/remove?rtype=file" -F file=@"/<PATH>/img1.png" -o "<PATH>/temp.file"
        curl -X POST -L "http://localhost:9090/replace?rtype=json" -F file_1=@"/<PATH>/img1.png" -F file_2=@"/<PATH>/img2.png" -o "<PATH>/temp.json"
        curl -X POST -L "http://localhost:9090/replace?rtype=file" -F file_1=@"/<PATH>/img1.png" -F file_2=@"/<PATH>/img2.png" -o "<PATH>/temp.png"
    
    """

    if request.method == "GET":
        if infer_type != "remove" and infer_type != "replace":
            raise SanicException(message="Invalid Infer Type", status_code=400)
        
        return JSONResponse(
            body={
                "statusText" : f"{infer_type.title()} endpoint of BG-Remove-API",
            },
            status=200,
        )
    elif request.method == "POST":
        rtype: Union[str, None] = request.args.get("rtype", None)
        if rtype is None:
            raise SanicException(message="No return type specified", status_code=400)
        
        if infer_type == "remove":
            filename: str = request.files.get("file").name

            image = Processor().decode_image(request.files.get("file").body)

            mask = Model().infer(image=image)
            for i in range(3): image[:, :, i] = image[:, :, i] & mask

            if rtype == "json":
                return JSONResponse(
                    body={
                        "statusText" : "Background Removal Successful",
                        "bglessImageData" : Processor.encode_image_to_base64(image=image),
                    },
                    status=201,
                )    
            elif rtype == "file":
                Processor.write_to_temp(image, f"TEMP/temp-{filename.split('.')[0]}.png")
                return await file(location=f"TEMP/temp-{filename.split('.')[0]}.png", status=201, mime_type="image/*")
        
        elif infer_type == "replace":
            filename_1: str = request.files.get("file_1").name
            filename_2: str = request.files.get("file_2").name

            image_1 = Processor.decode_image(request.files.get("file_1").body)
            image_2 = Processor.decode_image(request.files.get("file_2").body)

            mask = Model().infer(image=image_1)
            mh, mw = mask.shape
            image_2 = Processor.preprocess_replace_bg_image(image_2, mw, mh)

            for i in range(3): 
                image_1[:, :, i] = image_1[:, :, i] & mask
                image_2[:, :, i] = image_2[:, :, i] & (255 - mask) 

            image_2 += image_1 

            if rtype == "json":
                return JSONResponse(
                    body={
                        "statusText" : "Background Replacement Successful",
                        "bgreplaceImageData" : Processor.encode_image_to_base64(image=image_2),
                    },
                    status=201,
                )
            elif rtype == "file":
                Processor.write_to_temp(image_2, f"TEMP/temp-{filename_1.split('.')[0]}-{filename_2.split('.')[0]}.png")
                return await file(location=f"TEMP/temp-{filename_1.split('.')[0]}-{filename_2.split('.')[0]}.png", status=201, mime_type="image/*")
        
        else:
            raise SanicException(message="Invalid Infer Type", status_code=404)


@app.route("/<infer_type:str>/li", methods=["GET", "POST"])
async def processing_li(request: Request, infer_type: str) -> JSONResponse:
    """
    BASH

        curl -X POST -L "http://localhost:9090/remove/li?rtype=json" -F file=@"/<PATH>/img1.png" -o "<PATH>/temp.json"
        curl -X POST -L "http://localhost:9090/remove/li?rtype=file" -F file=@"/<PATH>/img1.png" -o "<PATH>/temp.file"
        curl -X POST -L "http://localhost:9090/replace/li?rtype=json" -F file_1=@"/<PATH>/img1.png" -F file_2=@"/<PATH>/img2.png" -o "<PATH>/temp.json"
        curl -X POST -L "http://localhost:9090/replace/li?rtype=file" -F file_1=@"/<PATH>/img1.png" -F file_2=@"/<PATH>/img2.png" -o "<PATH>/temp.png"
    
    """
    
    if request.method == "GET":
        if infer_type != "remove" and infer_type != "replace":
            raise SanicException(message="Invalid Infer Type", status_code=400)
        
        return JSONResponse(
            body={
                "statusText" : f"{infer_type.title()} lightweight endpoint of BG-Remove-API",
            },
            status=200,
        )
    
    elif request.method == "POST":
        rtype: Union[str, None] = request.args.get("rtype", None)
        if rtype is None:
            raise SanicException(message="No return type specified", status_code=400)
        
        if infer_type == "remove":
            filename: str = request.files.get("file").name

            image = Processor.decode_image(request.files.get("file").body)

            mask = Model(lightweight=True).infer(image=image)
            for i in range(3): image[:, :, i] = image[:, :, i] & mask

            if rtype == "json":
                return JSONResponse(
                    body={
                        "statusText" : "Background Removal Successful",
                        "bglessImageData" : Processor.encode_image_to_base64(image=image),
                    },
                    status=200,
                )
            elif rtype == "file":
                Processor.write_to_temp(image, f"TEMP/temp-{filename.split('.')[0]}.png")
                return await file(location=f"TEMP/temp-{filename.split('.')[0]}.png", status=201, mime_type="image/*")
        
        elif infer_type == "replace":
            filename_1: str = request.files.get("file_1").name
            filename_2: str = request.files.get("file_2").name

            image_1 = Processor.decode_image(request.files.get("file_1").body)
            image_2 = Processor.decode_image(request.files.get("file_2").body)

            mask = Model(lightweight=True).infer(image=image_1)
            mh, mw = mask.shape
            image_2 = Processor.preprocess_replace_bg_image(image_2, mw, mh)

            for i in range(3): 
                image_1[:, :, i] = image_1[:, :, i] & mask
                image_2[:, :, i] = image_2[:, :, i] & (255 - mask) 

            image_2 += image_1   

            if rtype == "json":
                return JSONResponse(
                    body={
                        "statusText" : "Background Replacement Successful",
                        "bgreplaceImageData" : Processor.encode_image_to_base64(image=image_2),
                    },
                    status=200,
                )
            elif rtype == "file":
                Processor.write_to_temp(image_2, f"TEMP/temp-{filename_1.split('.')[0]}-{filename_2.split('.')[0]}.png")
                return await file(location=f"TEMP/temp-{filename_1.split('.')[0]}-{filename_2.split('.')[0]}.png", status=201, mime_type="image/*")
        
        else:
            raise SanicException(message="Invalid Infer Type", status_code=404)


if __name__ == "__main__":
    args_1: str = "--mode"
    args_2: str = "--port"
    args_3: str = "--workers"

    mode: str = "local-machine"
    port: int = 9090
    workers: int = 1

    if args_1 in sys.argv:
        mode = sys.argv[sys.argv.index(args_1) + 1]
    if args_2 in sys.argv:
        port = int(sys.argv[sys.argv.index(args_2) + 1])
    if args_3 in sys.argv:
        workers = int(sys.argv[sys.argv.index(args_3) + 1])
    
    if mode == "local-machine":
        app.run(host="localhost", port=port, dev=True, workers=workers)

    elif mode == "local":
        app.run(host="0.0.0.0", port=port, dev=True, workers=workers)

    elif mode == "render":
        app.run(host="0.0.0.0", port=port, single_process=True, access_log=True)

    elif mode == "prod":
        app.run(host="0.0.0.0", port=port, dev=False, workers=workers, access_log=True)

    else:
        raise ValueError("Invalid Mode")