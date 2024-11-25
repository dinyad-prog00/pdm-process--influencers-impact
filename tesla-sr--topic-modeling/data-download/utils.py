from langdetect import detect, DetectorFactory

# Ensure consistent language detection results
DetectorFactory.seed = 0


# Function to check if a comment is in English.
def comment_is_in_english(comment):
    text = comment["textDisplay"]
    try:
        detected_language = detect(text)
        return detected_language == "en"
    except Exception as e:
        # print(f"Error detecting language: {e}")
        return False


# Function to get replies for a specific comment
def get_replies(youtube, parent_id):
    replies = []
    next_page_token = None

    while True:
        reply_request = youtube.comments().list(
            part="snippet",
            parentId=parent_id,
            textFormat="plainText",
            maxResults=100,
            pageToken=next_page_token,
        )
        reply_response = reply_request.execute()

        for item in reply_response["items"]:
            comment = item["snippet"]
            if comment_is_in_english(comment):
                replies.append(
                    {
                        "id": item["id"],
                        "comment": comment["textDisplay"],
                        "authorDisplayName": comment["authorDisplayName"],
                        "authorChannelUrl": comment["authorChannelUrl"],
                        "likeCount": comment["likeCount"],
                        "totalReplyCount": 0,
                        "parentId": parent_id,
                        "publishedAt": comment["publishedAt"],
                        "updatedAt": (
                            comment["updatedAt"]
                            if "updatedAt" in comment
                            else comment["publishedAt"]
                        ),
                    }
                )

        next_page_token = reply_response.get("nextPageToken")
        if not next_page_token:
            break

    return replies


# Function to get all comments (including replies) for a single video
def get_comments_for_video(youtube, video_id):
    all_comments = []
    next_page_token = None

    while True:
        comment_request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            pageToken=next_page_token,
            textFormat="plainText",
            maxResults=100,
        )
        comment_response = comment_request.execute()

        for item in comment_response["items"]:
            top_comment = item["snippet"]["topLevelComment"]["snippet"]
            if comment_is_in_english(top_comment):
                all_comments.append(
                    {
                        "id": item["snippet"]["topLevelComment"]["id"],
                        "comment": top_comment["textDisplay"],
                        "authorDisplayName": top_comment["authorDisplayName"],
                        "authorChannelUrl": top_comment["authorChannelUrl"],
                        "likeCount": top_comment["likeCount"],
                        "totalReplyCount": item["snippet"]["totalReplyCount"],
                        "publishedAt": top_comment["publishedAt"],
                        "updatedAt": (
                            top_comment["updatedAt"]
                            if "updatedAt" in top_comment
                            else top_comment["publishedAt"]
                        ),
                    }
                )

            # Fetch replies if there are any
            if item["snippet"]["totalReplyCount"] > 0:
                all_comments.extend(
                    get_replies(youtube, item["snippet"]["topLevelComment"]["id"])
                )

        next_page_token = comment_response.get("nextPageToken")
        if not next_page_token:
            break

    return all_comments
