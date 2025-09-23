import json
import base64
import os
import boto3
from fastapi import APIRouter, HTTPException
from sell_my_stuff.api.models.models import AnalyzeImageRequest, AnalyzeImageResponse

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeImageResponse)
async def analyze_image(request: AnalyzeImageRequest):
    """
    Analyze an image and generate a sales-optimized listing description and price suggestion.
    """
    try:
        # Initialize Bedrock client
        bedrock = boto3.client('bedrock-runtime', region_name=os.getenv('AWS_REGION', 'eu-central-1'))
        
        # Validate and clean base64 image data
        try:
            # Remove data URL prefix if present (e.g., "data:image/jpeg;base64,")
            if ',' in request.image:
                image_base64 = request.image.split(',')[1]
            else:
                image_base64 = request.image
            
            # Validate that it's valid base64
            base64.b64decode(image_base64)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")

        model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "model_id": model_id,
            "max_tokens": 1000,
            "system": "You are an expert at creating compelling online marketplace listings. Analyze the provided image...",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": "Please analyze this item and provide a sales-optimized description and price suggestion in JSON format."
                        }
                    ]
                }
            ]
        }
        
        try:
            response = bedrock.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                contentType="application/json"
            )
            
            response_body = json.loads(response['body'].read())
            analysis_text = response_body['content'][0]['text']
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to analyze image with Bedrock: {str(e)}")
        
        # Parse the JSON response
        try:
            analysis_data = json.loads(analysis_text)
            description = analysis_data.get('description', '')
            suggested_price = analysis_data.get('suggested_price', '')
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Failed to parse AI response as JSON: {str(e)}")

        return AnalyzeImageResponse(
            success=True,
            message="Image analyzed successfully",
            description=description,
            suggested_price=suggested_price
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing image: {str(e)}")
