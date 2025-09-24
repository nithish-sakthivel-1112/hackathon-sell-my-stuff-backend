# listings.py
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

            # Validate base64 decoding
            base64.b64decode(image_base64)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")

        # --- IMPORTANT: use the *inference profile* ARN for Nova Pro (replace with the exact ARN from Bedrock UI) ---
        model_id = "arn:aws:bedrock:eu-central-1:536607082495:inference-profile/eu.amazon.nova-pro-v1:0"

        # Build request body in the Bedrock format for Amazon Nova (multimodal)
        # Use `input` with `messages` and an `inferenceConfig` block for throughput/limits.
        body = {
            "input": {
                "messages": [
                    {
                        "role": "system",
                        "content": [
                            {
                                "type": "text",
                                "text": "You are an expert at creating compelling online marketplace listings. Analyze the provided image and return a JSON object containing 'description' and 'suggested_price'. Keep the JSON minimal and machine-parseable."
                            }
                        ],
                    },
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
            },
            # Put model limits / tuning in inferenceConfig (not top-level max_tokens)
            "inferenceConfig": {
                "maxTokens": 1000,
                "temperature": 0.2
            }
        }

        try:
            response = bedrock.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                contentType="application/json"
            )

            # `response['body']` is a StreamingBody; read it and parse JSON
            raw = response['body'].read()
            response_body = json.loads(raw)

            # Different Bedrock models / profiles may return different shapes.
            # Try several possible paths safely.
            analysis_text = None

            # Common shapes:
            # 1) response_body.get('outputs')[0]['content'][0]['text']
            # 2) response_body.get('content')[0]['text']
            # 3) response_body.get('outputs')[0]['content'][0]['message']['content'][0]['text'] (rare)
            if isinstance(response_body, dict):
                # Try outputs -> content -> text
                outputs = response_body.get('outputs') or []
                if outputs and isinstance(outputs, list):
                    first_out = outputs[0]
                    content = first_out.get('content') or []
                    if content and isinstance(content, list):
                        # find first item that has text
                        for c in content:
                            if isinstance(c, dict) and 'text' in c:
                                analysis_text = c['text']
                                break
                            # some shapes embed message->content:
                            if c.get('type') == 'message' and isinstance(c.get('message'), dict):
                                msg_content = c['message'].get('content') or []
                                for mc in msg_content:
                                    if isinstance(mc, dict) and 'text' in mc:
                                        analysis_text = mc['text']
                                        break
                                if analysis_text:
                                    break

                # fallback: top-level 'content'
                if not analysis_text and 'content' in response_body:
                    cont = response_body.get('content') or []
                    if cont and isinstance(cont, list) and 'text' in cont[0]:
                        analysis_text = cont[0]['text']

            # final fallback: try direct text field
            if not analysis_text:
                # search recursively for first 'text' value
                def find_first_text(obj):
                    if isinstance(obj, dict):
                        if 'text' in obj and isinstance(obj['text'], str):
                            return obj['text']
                        for v in obj.values():
                            res = find_first_text(v)
                            if res:
                                return res
                    elif isinstance(obj, list):
                        for item in obj:
                            res = find_first_text(item)
                            if res:
                                return res
                    return None
                analysis_text = find_first_text(response_body)

            if not analysis_text:
                raise HTTPException(status_code=500, detail=f"Could not find text output in Bedrock response: {json.dumps(response_body)[:1000]}")

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to analyze image with Bedrock: {str(e)}")

        # Parse the JSON response text returned by the model
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
