from flask import Blueprint, render_template, abort
import config

main_bp = Blueprint("main", __name__)

@main_bp.context_processor
def inject_brand():
    return {"brand": config.BRAND, "slogan": config.SLOGAN}

@main_bp.route("/")
def index():
    return render_template("index.html", product=config.PRODUCTS[0])

@main_bp.route("/san-pham")
@main_bp.route("/san-pham/<slug>")
def product(slug=None):
    p = next((x for x in config.PRODUCTS if x["slug"] == (slug or x["slug"])), None)
    if not p:
        abort(404)
    return render_template("product.html", product=p)

@main_bp.route("/huong-dan")
def howto():
    return render_template("howto.html", product=config.PRODUCTS[0])

@main_bp.route("/ve-chung-toi")
def about():
    return render_template("about.html")
