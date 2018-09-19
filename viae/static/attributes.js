const label_attributes = {
    "region": {
        "label": {
            "type": "dropdown",
            "description": "Label (class) of object",
            "options": {
                "bag": "Bag",
                "dress": "Dress",
                "hat": "Hat",
                "jacket": "Jacket",
                "shoe": "Shoe",
                "skirt": "Skirt",
                "top": "Top",
                "trousers": "Trousers",
                "unknown": "Unknown (object)"
            },
            "default_options": {
                "unknown": true
            }
        }
    },
    "file": { // NB: might be removed if not needed
        "caption": {
            "type": "text",
            "description": "",
            "default_value": ""
        },
        "public_domain": {
            "type": "radio",
            "description": "",
            "options": {
                "yes": "Yes",
                "no": "No"
            },
            "default_options": {
                "no": true
            }
        },
        "image_url": {
            "type": "text",
            "description": "",
            "default_value": ""
        }
    }
}