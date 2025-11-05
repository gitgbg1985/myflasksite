from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import plotly.express as px
import requests
import openpyxl

app = Flask(__name__)
app.secret_key = "replace-this-secret-key"

@app.route("/")
def home():
    return render_template("index.html")

#@app.route("/charts")
#def charts():
#    df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv")
#    fig = px.line(df, x="Date", y="AAPL.Close", title="Apple Closing Price")
#    chart_html = fig.to_html(full_html=False)
#    return render_template("charts.html", chart=chart_html)
@app.route("/charts")
def charts():
    # 1️⃣ Fetch Apple dataset (always latest from GitHub)
    df_apple = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv")
    fig_apple = px.line(
        df_apple,
        x="Date",
        y="AAPL.Close",
        title="Apple Closing Price"
    )
    chart_apple_html = fig_apple.to_html(full_html=False)

    # 2️⃣ Fetch IDA IPCA Infraestrutura dataset (always latest from S3)
    url_ida = "https://s3-data-prd-use1-precos.s3.us-east-1.amazonaws.com/arquivos/indices-historico/IDAIPCAINFRAESTRUTURA-HISTORICO.xls"
    df_ida = pd.read_excel(url_ida)

    # Clean and prepare
    df_ida["Data de Referência"] = pd.to_datetime(df_ida["Data de Referência"], errors="coerce")
    df_ida = df_ida.sort_values("Data de Referência")

    fig_ida = px.line(
        df_ida,
        x="Data de Referência",
        y="Número Índice",
        title="IDA IPCA Infraestrutura - Número Índice ao longo do tempo"
    )
    chart_ida_html = fig_ida.to_html(full_html=False)

    # Render both charts
    return render_template("charts.html", chart_apple=chart_apple_html, chart_ida=chart_ida_html)

@app.route("/news")
def news():
    resp = requests.get("https://hn.algolia.com/api/v1/search?query=data")
    articles = resp.json().get("hits", [])[:10]
    return render_template("news.html", articles=articles)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["password"] == "mypassword":
            session["user"] = True
            return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if not session.get("user"):
        return redirect(url_for("login"))
    return render_template("dashboard.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)

