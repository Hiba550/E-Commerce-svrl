"""
Utility script to set a product's `model_url` field to a model file under `static/`.

Usage (PowerShell):
    python set_model_for_product.py --slug some-product-slug --model-path models/sample.glb

Place your GLB at: static/models/sample.glb
If you prefer to use a product id:
    python set_model_for_product.py --id 1 --model-path models/sample.glb
"""
import os
import argparse

from app import create_app
from models import db, Product


def main():
    parser = argparse.ArgumentParser(description='Set product.model_url to a static model file')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--slug', help='Product slug to update')
    group.add_argument('--id', type=int, help='Product ID to update')
    parser.add_argument('--model-path', required=True,
                        help="Path relative to project's static folder, e.g. 'models/sample.glb' or '/static/models/sample.glb'")
    parser.add_argument('--config', default='development', help='Flask config name (default: development)')

    args = parser.parse_args()

    # Normalize model_path: remove leading /static/ if present
    model_path = args.model_path
    if model_path.startswith('/static/'):
        model_path = model_path[len('/static/'):]
    if model_path.startswith('static/'):
        model_path = model_path[len('static/'):]

    app = create_app(args.config)

    with app.app_context():
        static_abs = app.static_folder  # typically <project>/static
        model_abs = os.path.join(static_abs, model_path)

        if not os.path.isfile(model_abs):
            print(f"Model file not found at: {model_abs}")
            print("Please place your .glb/.gltf file under the project's static folder (e.g. static/models/sample.glb) and re-run")
            return

        if args.slug:
            product = Product.query.filter_by(slug=args.slug).first()
        else:
            product = Product.query.get(args.id)

        if not product:
            print('Product not found. Provide a valid --slug or --id that exists in the database.')
            return

        # Save the relative path (without leading slash). Templates handle either '/static/...' or relative paths.
        product.model_url = model_path
        db.session.commit()

        print(f"Updated product (id={product.id}, slug={product.slug}) model_url -> '{product.model_url}'")
        print('You can now start the dev server and view the product on the products list or detail page.')


if __name__ == '__main__':
    main()
