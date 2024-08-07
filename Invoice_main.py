import json

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()  # load all the environment variables from .env.

import streamlit as st
import os
from PIL import Image
import google.generativeai as genai
from langchain.prompts import FewShotPromptTemplate
import time

GOOGLE_API_KEY = "Enter your api key here"
genai.configure(api_key=GOOGLE_API_KEY)  # load api and assign

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    }
]

MODEL_CONFIG = {
    "temperature": 0.4}

# model = genai.GenerativeModel("gemini-pro-vision")     # initilize the model
model = genai.GenerativeModel(model_name="gemini-1.5-pro",
                              generation_config=MODEL_CONFIG,
                              safety_settings=None)
model2 = genai.GenerativeModel(model_name="gemini-pro")
model3 = genai.GenerativeModel('gemini-1.5-flash',
                               generation_config={"response_mime_type": "application/json"})



System_prompt = """Reformat the invoice data in json format to ensure it's easily comprehensible for humans in a single read-through. 
                  Additionally, structure it in a way that allows a machine learning model to accurately parse the data and 
                  generate answers to specific questions

                  Refer example to extract information-

                  "Vendor":
                                Company: Everchem Specialty Chemicals
                                Address: 1400 N. Providence Rd., Suite 302, Media, PA 19063
                                Phone: 484-234-5030
                                Fax: 484-234-5037
                                Website: www.everchem.com

                  "Question": "What is the saller/vendor address
                  "Answer": "1400 N. Providence Rd., Suite 302, Media, PA 19063"

                  """


def get_data_json(image):
    user_prompt = ""
    output = get_gemini_response(System_prompt, image, user_prompt)
    return (output)


def get_all_keys(data, key_list=[]):
    if isinstance(data, dict):
        for key in data:
            key_list.append(key.lower())
            get_all_keys(data[key], key_list)  # Recursive call with the same list
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                get_all_keys(item, key_list)  # Handle dictionaries within lists
    return key_list


def lower_keys(data):
    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            new_data[key.lower()] = lower_keys(value)  # Recursive call
        return new_data
    elif isinstance(data, list):
        # Handle lists containing dictionaries
        return [lower_keys(item) if isinstance(item, dict) else item for item in data]
    else:
        return data  # Return non-dictionary, non-list values unchanged


def get_gemini_response(input, image, prompt):
    # time.sleep(5)
    response = model.generate_content([input, image[0], prompt])
    json_data = response.candidates

    start_index = str(json_data).find("text:")
    print(start_index, "the start index in this is:")

    if (start_index > 30 and start_index < 40):
        st.write("Wait Response is loading...")
        time.sleep(5)
        return response.text
    else:
        time.sleep(5)
        response = model.generate_content([System_prompt, image[0]])
        print("This is Coming in else condition")
        st.write(response.text)

        mode = json.load(response.text)
        print(mode, "The mode is this")


# it'll take uploaded file convert into bytes and give all the image info in bytes
def input_image_details(uploaded_file):
    if uploaded_file is not None:
        # read the file into bytes
        bytes_data = uploaded_file.getvalue()

        image_parts = [
            {
                "mime_type": uploaded_file.type,  # get the mine type of the uploaded file
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")


##initialize our streamlit app

st.set_page_config(page_title="Multilanguage Invoice Extractor")

st.header("Multilanguage Invoice Extractor")
uploaded_file = st.file_uploader("Choose an image of the invoice...", type=["jpg", "jpeg", "png"])
image = ""

if uploaded_file is not None:
    image = Image.open(uploaded_file)  # to upload file
    st.image(image, caption="Uploaded Image.", use_column_width=True)  # To diplaying the uploaded file
    input = st.text_input("Input Prompt: ", key="input")

submit = st.button("Tell me the invoice")  # submit button



# You are an expert in understanding invoices. we will upload a image as invoice and you will have to answer any question based on the uploaded invoice image
input_prompt = """
You possess expertise in invoice comprehension. When presented with an uploaded invoice image, your task is to respond 
to inquiries based on the content of the invoice. Your responses should address any questions regarding the information 
contained within the uploaded invoice image.

Refer this example for more:
    Example 1 - 
    "Question" : "Give the content of Description column"
    "Answer" : "DESCRIPTION
                Polymeric MDI, (500 lb Drums)-40 drums
                Purchasing: 40 drums MDI MR-200
                Purchase Price $1.00 per b
                Pick up Location: Fontana CA- please confirm this location
                DRUMS MUST BE PALLETIZED AND SHRINK-WRAPPED AND/OR BANDED BOL will be provided by Nadja
                BOL Destination:
                Green Insulation Technologies
                Chadwick Insulation 1184 West Division Street Westville, OK 74965
                Contact: Steve Phone: 918-797-0010
                Delivery PO# 12062022-Rel1"

    Example 2 - 
    Ship To : Everest Systems LLC
              16601 Central Green Blvd #100
              Houston, TX 77032
              United States

    Question - What is the ship to address in the invoice
    Answer -   Everest Systems LLC
              16601 Central Green Blvd #100
              Houston, TX 77032
              United States 
    """

# If submit button is clicked
if submit:
    image_data = input_image_details(uploaded_file)
    # response = get_gemini_response(input_prompt,image_data,input,few_shot_examples)
    st.subheader("The Response is")

    response = get_gemini_response(input_prompt, image_data, input)

    st.write(response)









# few_shot_examples = [
#     {
#     "Table":    """
#                      | Quality | item        | Description                                      | Unit Price   |  Total
#                      |         |             |                                                  | 270084       |  82,34188
#                      | 39,682  | Import Toll | Payment terms                                    |              |
#                      |         |             | GRID RESISTOR ASSEMBLY 607-1316 RLA 200-240V     |              |
#                      |         |             | GRID RESISTOR ASSEMBLY 607-1316 RLA 346-480V     |              |
#                      |         |             | Resistor EWR2-R18A-1D00-BH                       |              |
#                 """,
#
#     "Question" : "Give the content of Description column?",
#     "Answer" : """Payment terms
#                GRID RESISTOR ASSEMBLY 607-1316 RLA 200-240V
#                GRID RESISTOR ASSEMBLY 607-1316 RLA 346-480V
#                Resistor EWR2-R18A-1D00-BH  """
#     },
#
#     {
#         "Table": """
#                      | Quality | item        | Description                                      | Unit Price   |  Total
#                      |         |             |                                                  | 270084       |  82,34188
#                      | 39,682  | Import Toll | Payment terms                                    |              |
#                      |         |             | GRID RESISTOR ASSEMBLY 607-1316 RLA 200-240V     |              |
#                      |         |             | GRID RESISTOR ASSEMBLY 607-1316 RLA 346-480V     |              |
#                      |         |             | Resistor EWR2-R18A-1D00-BH                       |              |
#                 """,
#
#         "Question": "What is the Description of item Import Toll?",
#         "Answer": """Payment terms
#                GRID RESISTOR ASSEMBLY 607-1316 RLA 200-240V
#                GRID RESISTOR ASSEMBLY 607-1316 RLA 346-480V
#                Resistor EWR2-R18A-1D00-BH  """
#
#     },
# ]

# few_shot_prompt = FewShotPromptTemplate(
#         examples = few_shot_examples,
#          # These variables are used in the prefix and suffix
#     )



# Important Prompts

# Page
# What is the shipping address of this invoice, give full address    or     What is the ship to address in the invoice
# # The invoice is from which company, give full address of the company   or     What is the Vendor address of this invoice, give full address     or          What is the vendor's address of this invoice, give full address


# What is the Send Invoice address? -          or          What is the Customer Address in the invoice
# give the description of the invoice in bullet points -
# What is the shipping address company name
# The invoice is TO which comapny?
# Who made the purchase order?
# What is the Description of the ITEM?                 or    Give the content of Description column
# What is the ship to address from the invoice in this image.     or       What is the ship to address in the invoice
# Provide receiver company details
# provide all the phone number present in the invoice and list down all associated details with phone number also?
# What is the from name?


# Give the description of line 1
