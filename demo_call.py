import requests
import json
import base64
from PIL import Image
import io

# Get demo data
response = requests.get("http://localhost:5000/api/demo")
data = response.json()

# Print concentration result
print(f"Concentration: {data['concentration']}±{data['uncertainty']}mg")

# If you want to display the plot image:
if "plot" in data:
    image_data = base64.b64decode(data["plot"])
    image = Image.open(io.BytesIO(image_data))
    image.show()
