import os
from flask import Flask, request, jsonify, render_template, Response
from flask_weasyprint import HTML, render_pdf

from dotenv import load_dotenv
from scripts.youtube_sentiment import get_video_data, get_latest_comments, analyze_sentiment
import plotly.graph_objects as go

# Force load .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    print("✅ .env file loaded successfully!")
else:
    print("❌ .env file NOT found! Please ensure the .env file exists and contains the required keys.")


app = Flask(__name__, static_url_path='/static')  # Enable static file serving


# Fetch API Key
# app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

api_key = os.getenv("API_KEY")

print(f"🔍 Loaded API Key: {api_key}")  # Debugging line

@app.route('/')
def home():
    return render_template('index.html', video_data=None, sentiment_analysis=None)


@app.route('/analyze', methods=['POST'])  # Handle POST request for video analysis

def analyze_video():
    video_id = request.form.get("video_id")  # Fetch video_id from POST form data
    if not video_id:
        return jsonify({"error": "Missing video_id parameter. Please provide a valid video ID."}), 400


    video_data = get_video_data(video_id)  # Fetch video data using the provided video ID

    if not video_data:
        return jsonify({"error": "Invalid Video ID. Please check the video ID and try again."}), 404


    # Fetch comments and perform sentiment analysis
    comments = get_latest_comments(video_id)
    sentiment_analysis = analyze_sentiment(comments) if comments else []  # Perform sentiment analysis on the fetched comments



    # Normalize sentiment values
    sentiment_counts = {"Positive": 0, "Negative": 0, "Neutral": 0}

    for result in sentiment_analysis:
        sentiment = result["sentiment"]
        
        # Normalize the sentiment values if there are any emojis or unexpected characters
        if "Positive" in sentiment:
            sentiment = "Positive"
        elif "Negative" in sentiment:
            sentiment = "Negative"
        elif "Neutral" in sentiment:
            sentiment = "Neutral"

        sentiment_counts[sentiment] += 1

    # Create a pie chart for sentiment analysis
    labels = ['Positive', 'Negative', 'Neutral']
    values = [sentiment_counts['Positive'], sentiment_counts['Negative'], sentiment_counts['Neutral']]

    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    graph_html = fig.to_html(full_html=False)

    # Create a bar chart for sentiment analysis
    bar_fig = go.Figure(data=[
        go.Bar(name='Sentiment Counts', x=labels, y=values)
    ])
    bar_graph_html = bar_fig.to_html(full_html=False)

    # Save the analyzed data to a text file
    report_content = f"Video Title: {video_data['title']}\n"
    report_content += f"Views: {video_data['views']}\n"
    report_content += f"Likes: {video_data['likes']}\n"
    report_content += f"Comments: {video_data['comments']}\n"
    report_content += "Sentiment Analysis:\n"

    for result in sentiment_analysis:
        report_content += f"Comment: {result['comment']}, Sentiment: {result['sentiment']}\n"

    # Write the report content to a file
    report_filename = f"report_{video_id}.txt"
    with open(report_filename, "w", encoding="utf-8") as report_file:
        report_file.write(report_content)

    response = {
        "video_data": video_data,
        "sentiment_analysis": sentiment_analysis,

        "title": video_data["title"],
        "views": video_data["views"],
        "likes": video_data["likes"],
        "comments": video_data["comments"],
        "sentiment_analysis": sentiment_analysis,
        "graph_html": graph_html
    }

    # Render results in the template
    return render_template('index.html', video_data=video_data, sentiment_analysis=sentiment_analysis, graph_html=graph_html, bar_graph_html=bar_graph_html)
    
    # Debugging: Log the response being sent to the template
    print(f"Response sent: {response}")

@app.route('/download_report', methods=['GET'])
def download_report():
    """Generates and downloads a report of the video analysis as a PDF."""
    video_data = request.args.get("video_data")  # Assuming video_data is passed as a query parameter
    sentiment_analysis = request.args.get("sentiment_analysis")  # Assuming sentiment_analysis is passed as a query parameter

    # Debugging: Log the received parameters
    print(f"Received video_data: {video_data}")
    print(f"Received sentiment_analysis: {sentiment_analysis}")

    if not video_data or not sentiment_analysis:
        return jsonify({"error": "Missing video_data or sentiment_analysis parameters."}), 400

        return jsonify({"error": "Missing video_data or sentiment_analysis parameters."}), 400

        return jsonify({"error": "Missing video_data or sentiment_analysis parameters."}), 400

        return jsonify({"error": "Missing video_data or sentiment_analysis parameters."}), 400

        return jsonify({"error": "Missing video_data or sentiment_analysis parameters."}), 400

        return jsonify({"error": "Missing video_data or sentiment_analysis parameters."}), 400

        return jsonify({"error": "Missing video_data or sentiment_analysis parameters."}), 400

        return jsonify({"error": "Missing video_data or sentiment_analysis parameters."}), 400

        return jsonify({"error": "Missing video_data or sentiment_analysis parameters."}), 400

        return jsonify({"error": "Missing video_data or sentiment_analysis parameters."}), 400

        return jsonify({"error": "Missing video_data or sentiment_analysis parameters."}), 400

        return jsonify({"error": "Missing video_data or sentiment_analysis parameters."}), 400





        return jsonify({"error": "Missing video_data or sentiment_analysis parameters."}), 400

    # Prepare the HTML content for the PDF
    report_content = render_template('report_template.html', video_data=video_data, sentiment_analysis=sentiment_analysis)


    # Generate PDF
    return render_pdf(HTML(string=report_content))

if __name__ == '__main__':
    app.run(debug=True)
