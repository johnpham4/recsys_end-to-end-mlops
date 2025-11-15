import gradio as gr
import pandas as pd
import json
from api import get_recommendations, get_user_item_sequence, push_new_item_sequence
from query import get_items_metadata_by_item, get_users
from theme import blueq

def parse_image_url(images_json_str):
    """Parse images JSON string and return the first image URL"""
    try:
        if pd.isna(images_json_str) or not images_json_str:
            return None

        images_dict = json.loads(images_json_str)

        # Try hi_res first, then large, then thumb
        for img_type in ['hi_res', 'large', 'thumb']:
            if img_type in images_dict:
                img_data = images_dict[img_type]

                # Handle string format like "['url1'\n 'url2'\n 'url3']"
                if isinstance(img_data, str):
                    if img_data.startswith('[') and img_data.endswith(']'):
                        # Remove outer brackets
                        img_data = img_data.strip('[]')
                        # Split by newlines and get first URL
                        for line in img_data.split('\n'):
                            line = line.strip()
                            if line:
                                # Remove quotes and extra spaces
                                url = line.strip("' \"")
                                if url and url.startswith('http'):
                                    return url
                    elif img_data.startswith('http'):
                        return img_data
                elif isinstance(img_data, list) and img_data:
                    return img_data[0]

        return None
    except Exception as e:
        print(f"Error parsing images: {e}")
        return None

# Fetch users
users = get_users()
sample_users = users[:10]

def get_item_df(selected_user):
    response = get_user_item_sequence(selected_user)
    item_sequences = response["item_sequence"]
    items_metadata = get_items_metadata_by_item(item_sequences)

    items_metadata = (
        items_metadata.set_index("item_id")
        .loc[item_sequences[::-1]]
        .reset_index()
        .reset_index()
        .rename(columns={"index": "recency_rank"})
    )
    return items_metadata

def get_recs(selected_user):
    recs = get_recommendations(selected_user, debug=False)
    recs_df = pd.DataFrame(recs["recommendations"])
    rec_item_ids = recs_df["rec_item_ids"].values.tolist()
    items_metadata = get_items_metadata_by_item(rec_item_ids)
    output = pd.merge(
        recs_df, items_metadata, how="left", left_on="rec_item_ids", right_on="item_id"
    )
    return output

def process_likes(*responses):
    # For more information on why we extract items based on these out of no where indices,
    # please refer to the below mention of process_likes in submit_button.click...
    recs_df = responses[-2]  # this is the current state of the recs_table
    user_id = responses[-1]  # this is the current selected user_id
    responses = responses[:-2]  # all the responses are behind those two last indices
    liked_items = []
    disliked_items = []
    item_sequences = []

    for i, r in enumerate(responses):
        if r is None:  # Skip if no selection
            continue

        title = recs_df.iloc[i]["title"]
        item_id = recs_df.iloc[i]["item_id"]
        item_display = f"{title} ({item_id})"

        if r == "👍 Like":
            liked_items.append(item_display)
            item_sequences.append(item_id)
        elif r == "👎 Dislike":
            disliked_items.append(item_display)
            item_sequences.append(item_id)

    # Only push to sequence if there are any ratings
    if item_sequences:
        push_new_item_sequence(user_id, item_sequences)

    result = ""
    if liked_items:
        liked_text = ", ".join(liked_items)
        result += f"You liked: {liked_text}\n"
    if disliked_items:
        disliked_text = ", ".join(disliked_items)
        result += f"You disliked: {disliked_text}\n"
    if not liked_items and not disliked_items:
        result = "No ratings selected. Please choose 👍 Like or 👎 Dislike for items."

    return result

with gr.Blocks(
    theme=gr.themes.Base(
        primary_hue=blueq,
        font=["Inter", "sans-serif"],
        font_mono=["Roboto Mono", "monospace"],
    )
) as demo:
    gr.Markdown("# RecSys MVP Demo")

    # Dropdown with autocomplete feature
    dropdown = gr.Dropdown(
        choices=sample_users,
        label="Who are you?",
        filterable=True,
        allow_custom_value=True,
        value="Select User ID",
    )
    user_id_select = gr.Button("Refresh Data", variant="secondary")

    # Output display as a DataFrame
    items_table = gr.DataFrame(label="Rated Items", interactive=False)

    recs_table = gr.DataFrame(label="Recommendations", interactive=False, visible=False)

    gr.HTML("<div style='height: 20px;'></div>")
    gr.Markdown("# Recommendations")

    @gr.render(inputs=recs_table)
    def show_rec_items(df):
        if df is None or df.empty or len(df) == 0:
            gr.Markdown("## No recommendations available. Please select a user and click 'Refresh Data'.")
        else:
            responses = []
            with gr.Row(equal_height=True):
                for _, row in df.iterrows():
                    title = row.get("title", "Unknown Title")
                    item_id = row.get("item_id", row.get("rec_item_ids", "Unknown ID"))
                    categories = row.get("categories", "Unknown Categories")
                    images = row.get("images", "")

                    # Parse image URL
                    image_url = parse_image_url(images)

                    with gr.Column(variant="panel"):
                        # Display image if available
                        if image_url:
                            gr.Image(value=image_url, height=150, width=150, show_label=False)
                        else:
                            gr.Markdown("*No image available*")

                        gr.Markdown(f"**{item_id}**")
                        gr.Markdown(f"### {title}")
                        gr.Markdown(f"*{categories}*")
                        response = gr.Radio(choices=["👍 Like", "👎 Dislike"], container=False)
                        responses.append(response)

            gr.HTML("<div style='height: 20px;'></div>")

            with gr.Column():
                submit_button = gr.Button("Submit Your Ratings", variant="primary")
                output = gr.Textbox(label="Ratings Recorded")
                submit_button.click(
                    process_likes,
                    # The intention here is to pass the relevant information to process_likes function
                    # So that it can push the new ratings to Feature Store for real-time feature updates
                    inputs=responses + [recs_table, dropdown],
                    outputs=output,
                )

    # Set up interaction
    user_id_select.click(get_item_df, dropdown, items_table)
    user_id_select.click(get_recs, dropdown, recs_table)
    dropdown.change(get_item_df, dropdown, items_table)
    dropdown.change(get_recs, dropdown, recs_table)

# Launch the interface
demo.launch()
