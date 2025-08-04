import json
import logging
from application.handler import handle_get_all_user_images, handle_get_all_images, handle_upload, handle_delete
from application.handler import create_response, authenticate_user
from domain.jwt_service import JWTService
from domain.image_service import ImageService
from repository.s3_repository import S3Repository
from config import Config

logger = logging.getLogger()
logger.setLevel(logging.ERROR)

def lambda_handler(event, context):
    logger.info("Lambda function invoked")
    logger.debug(f"Full event: {json.dumps(event)}")

    try:
        logger.info("Initializing services")
        jwt_service = JWTService()
        s3_repository = S3Repository()
        image_service = ImageService(s3_repository)
        logger.info("Services initialized successfully")

        http_method = event.get('httpMethod', '').upper()
        logger.info(f"Processing {http_method} request")

        headers = event.get('headers', {})
        path = event.get('path', '')
        logger.debug(f"Request path: {path}")
        header_region = headers.get('x-region')

        match path:
            case "/images/status":
                if http_method == "GET":
                    logger.info("Handling health check request")
                    return create_response(200, {
                        "status": "OK",
                        "message": "Service is operational"
                    })
                else:
                    return create_response(405, {"error": "Method not allowed"})

            case "/images":
                if http_method == "GET":
                    if not header_region or header_region.upper() not in Config.ALLOWED_REGIONS.split(','):
                        return create_response(403, {"error": f"Region {header_region} not allowed"})
                    logger.info(f"Fetching all images from region: {header_region}")
                    return handle_get_all_images(image_service)
                else:
                    return create_response(405, {"error": "Method not allowed"})

            case "/images/user":
                if http_method not in ("GET", "PUT", "DELETE"):
                    return create_response(405, {"error": "Method not allowed"})
                user, error_response = authenticate_user(headers, jwt_service)
                if error_response:
                    return error_response
                if http_method == "GET":
                    logger.info(f"Fetching images for user: {user.id}")
                    return handle_get_all_user_images(user, image_service)
                elif http_method == "PUT":
                    logger.info("Processing image upload")
                    return handle_upload(event, user, image_service)
                elif http_method == "DELETE":
                    try:
                        body = event.get('body')
                        if body is None:
                            return create_response(400, {"error": "Request body is required for image deletion"})
                        if isinstance(body, str):
                            body_json = json.loads(body)
                        else:
                            body_json = body
                        image_name = body_json.get('image_name')
                    except Exception as e:
                        logger.error(f"Failed to parse request body for image deletion: {str(e)}")
                        return create_response(400, {"error": "Invalid request body"})
                    if not image_name:
                        return create_response(400, {"error": "'image_name' field is required in request body"})
                    if not str(image_name).endswith((".jpg", ".jpeg", ".png")):
                        return create_response(400, {"error": "Invalid image name format. Allowed formats: .jpg, .jpeg, .png"})
                    logger.info("Processing image deletion")
                    return handle_delete(image_name, user, image_service)
                else:
                    return create_response(405, {"error": "Method not allowed"})

            case _:
                logger.warning(f"No route found for {http_method} {path}")
                return create_response(404, {"error": "Route not found"})

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return create_response(500, {"error": "Internal server error"})
