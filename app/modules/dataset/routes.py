import logging
import os
import json
import shutil
import tempfile
import uuid
from datetime import datetime, timezone
from zipfile import ZipFile

from app.modules.hubfile.services import HubfileService
from flamapy.metamodels.fm_metamodel.transformations import UVLReader, GlencoeWriter, SPLOTWriter
from flamapy.metamodels.pysat_metamodel.transformations import FmToPysat, DimacsWriter

from flask import (
    redirect,
    render_template,
    request,
    jsonify,
    send_from_directory,
    make_response,
    abort,
    url_for,
)
from flask_login import login_required, current_user

from app.modules.dataset.forms import DataSetForm
from app.modules.dataset.models import (
    DSDownloadRecord
)
from app.modules.dataset import dataset_bp
from app.modules.dataset.services import (
    AuthorService,
    DSDownloadRecordService,
    DSMetaDataService,
    DSViewRecordService,
    DataSetService,
    DOIMappingService
)
from app.modules.fakenodo.services import FakenodoService
from app.modules.auth.models import User

logger = logging.getLogger(__name__)


dataset_service = DataSetService()
author_service = AuthorService()
dsmetadata_service = DSMetaDataService()
fakenodo_service = FakenodoService()
doi_mapping_service = DOIMappingService()
ds_view_record_service = DSViewRecordService()


@dataset_bp.route("/dataset/upload", methods=["GET", "POST"])
@login_required
def create_dataset():
    form = DataSetForm()
    if request.method == "POST":

        dataset = None

        if not form.validate_on_submit():
            return jsonify({"message": form.errors}), 400

        try:
            logger.info("Parsing the UVL files to JSON...")

            mergedUVL = []
            for feature_model in form.feature_models:
                uvl_filename = feature_model.uvl_filename.data
                uvl_file_path = 'uploads/temp/' + str(current_user.id) + '/' + str(uvl_filename)
                splitted_filename = uvl_filename.split('.')
                aux = '{"' + splitted_filename[0] + '": ' + dataset_service.parse_uvl_to_json(uvl_file_path) + '}'
                aux = json.loads(aux)
                mergedUVL.append(aux)

            logger.info("All UVL files have been parsed to JSON")
        except Exception as exc:
            logger.exception(f"Exception while parsing UVL to JSON in local {exc}")
            return jsonify({"Exception while parsing UVL to JSON in local : ": str(exc)}), 400

        try:
            logger.info("Creating dataset...")
            dataset = dataset_service.create_from_form(form=form, current_user=current_user)
            logger.info(f"Created dataset: {dataset}")
            dataset_service.move_feature_models(dataset)
        except Exception as exc:
            logger.exception(f"Exception while create dataset data in local {exc}")
            return jsonify({"Exception while create dataset data in local: ": str(exc)}), 400

        deposition = fakenodo_service.create_new_deposition(dataset, mergedUVL)
        dataset_service.update_dsmetadata(
            dataset.ds_meta_data_id, deposition_id=deposition.id, dataset_doi=f'10.1234/dataset{dataset.id}'
        )

        # Delete temp folder
        file_path = current_user.temp_folder()
        if os.path.exists(file_path) and os.path.isdir(file_path):
            shutil.rmtree(file_path)

        msg = "Everything works!"
        return jsonify({"message": msg}), 200

    return render_template("dataset/upload_dataset.html", form=form)


@dataset_bp.route("/dataset/list", methods=["GET", "POST"])
@login_required
def list_dataset():
    return render_template(
        "dataset/list_datasets.html",
        datasets=dataset_service.get_synchronized(current_user.id),
        local_datasets=dataset_service.get_unsynchronized(current_user.id)
    )


@dataset_bp.route("/dataset/file/upload", methods=["POST"])
@login_required
def upload():
    file = request.files["file"]
    temp_folder = current_user.temp_folder()

    if not file or not file.filename.endswith(".uvl"):
        return jsonify({"message": "No valid file"}), 400

    # create temp folder
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    file_path = os.path.join(temp_folder, file.filename)

    if os.path.exists(file_path):
        # Generate unique filename (by recursion)
        base_name, extension = os.path.splitext(file.filename)
        i = 1
        while os.path.exists(
            os.path.join(temp_folder, f"{base_name} ({i}){extension}")
        ):
            i += 1
        new_filename = f"{base_name} ({i}){extension}"
        file_path = os.path.join(temp_folder, new_filename)
    else:
        new_filename = file.filename

    try:
        file.save(file_path)
    except Exception as e:
        return jsonify({"message": str(e)}), 500

    return (
        jsonify(
            {
                "message": "UVL uploaded and validated successfully",
                "filename": new_filename,
            }
        ),
        200,
    )


@dataset_bp.route("/dataset/file/delete", methods=["POST"])
def delete():
    data = request.get_json()
    filename = data.get("file")
    temp_folder = current_user.temp_folder()
    filepath = os.path.join(temp_folder, filename)

    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({"message": "File deleted successfully"})

    return jsonify({"error": "Error: File not found"})


@dataset_bp.route("/dataset/download/<int:dataset_id>", methods=["GET"])
def download_dataset(dataset_id):
    dataset = dataset_service.get_or_404(dataset_id)

    file_path = f"uploads/user_{dataset.user_id}/dataset_{dataset.id}/"

    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, f"dataset_{dataset_id}.zip")

    with ZipFile(zip_path, "w") as zipf:
        for subdir, dirs, files in os.walk(file_path):
            for file in files:
                full_path = os.path.join(subdir, file)

                relative_path = os.path.relpath(full_path, file_path)

                zipf.write(
                    full_path,
                    arcname=os.path.join(
                        os.path.basename(zip_path[:-4]), relative_path
                    ),
                )

    user_cookie = request.cookies.get("download_cookie")
    if not user_cookie:
        user_cookie = str(
            uuid.uuid4()
        )  # Generate a new unique identifier if it does not exist
        # Save the cookie to the user's browser
        resp = make_response(
            send_from_directory(
                temp_dir,
                f"dataset_{dataset_id}.zip",
                as_attachment=True,
                mimetype="application/zip",
            )
        )
        resp.set_cookie("download_cookie", user_cookie)
    else:
        resp = send_from_directory(
            temp_dir,
            f"dataset_{dataset_id}.zip",
            as_attachment=True,
            mimetype="application/zip",
        )

    # Check if the download record already exists for this cookie
    existing_record = DSDownloadRecord.query.filter_by(
        user_id=current_user.id if current_user.is_authenticated else None,
        dataset_id=dataset_id,
        download_cookie=user_cookie
    ).first()

    if not existing_record:
        # Record the download in your database
        DSDownloadRecordService().create(
            user_id=current_user.id if current_user.is_authenticated else None,
            dataset_id=dataset_id,
            download_date=datetime.now(timezone.utc),
            download_cookie=user_cookie,
        )

    return resp


@dataset_bp.route("/dataset/download/<int:dataset_id>/<string:format>", methods=["GET"])
def download_dataset_format(dataset_id, format):
    valid_formats = ["DIMACS", "GLENCOE", "SPLOT", "UVL"]

    if format not in valid_formats:
        response = jsonify({"error": "Formato de descarga no soportado"})
        response.status_code = 400
        return response

    dataset = dataset_service.get_or_404(dataset_id)

    file_path = f"uploads/user_{dataset.user_id}/dataset_{dataset.id}/"
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, f"dataset_{dataset_id}.zip")

    with ZipFile(zip_path, "w") as zipf:
        for subdir, dirs, files in os.walk(file_path):
            for file in dataset.files():
                full_path = os.path.join(subdir, file.name)

                with open(full_path, "r") as file_content:
                    content = file_content.read()

                if format == "DIMACS":
                    transformed_file_path, original_filename = transform_to_dimacs(file.id)
                    with open(transformed_file_path, "r") as transformed_file:
                        content = transformed_file.read()
                    new_filename = f"{original_filename}_cnf.txt"

                elif format == "GLENCOE":
                    transformed_file_path, original_filename = transform_to_glencoe(file.id)
                    with open(transformed_file_path, "r") as transformed_file:
                        content = transformed_file.read()
                    new_filename = f"{original_filename}_glencoe.txt"

                elif format == "SPLOT":
                    transformed_file_path, original_filename = transform_to_splot(file.id)
                    with open(transformed_file_path, "r") as transformed_file:
                        content = transformed_file.read()
                    new_filename = f"{original_filename}_splot.txt"
                elif format == "UVL":
                    new_filename = f"{file.name}"

                with zipf.open(new_filename, "w") as zipfile:
                    zipfile.write(content.encode())

    user_cookie = request.cookies.get("download_cookie")
    if not user_cookie:
        user_cookie = str(
            uuid.uuid4()
        )  # Generate a new unique identifier if it does not exist
        # Save the cookie to the user's browser
        resp = make_response(
            send_from_directory(
                temp_dir,
                f"dataset_{dataset_id}.zip",
                as_attachment=True,
                mimetype="application/zip",
            )
        )
        resp.set_cookie("download_cookie", user_cookie)
    else:
        resp = send_from_directory(
            temp_dir,
            f"dataset_{dataset_id}.zip",
            as_attachment=True,
            mimetype="application/zip",
        )

    # Check if the download record already exists for this cookie
    existing_record = DSDownloadRecord.query.filter_by(
        user_id=current_user.id if current_user.is_authenticated else None,
        dataset_id=dataset_id,
        download_cookie=user_cookie
    ).first()

    if not existing_record:
        # Record the download in your database
        DSDownloadRecordService().create(
            user_id=current_user.id if current_user.is_authenticated else None,
            dataset_id=dataset_id,
            download_date=datetime.now(timezone.utc),
            download_cookie=user_cookie,
        )

    return resp


@dataset_bp.route("/doi/<path:doi>/", methods=["GET"])
def subdomain_index(doi):

    # Check if the DOI is an old DOI
    new_doi = doi_mapping_service.get_new_doi(doi)
    if new_doi:
        # Redirect to the same path with the new DOI
        return redirect(url_for('dataset.subdomain_index', doi=new_doi), code=302)

    # Try to search the dataset by the provided DOI (which should already be the new one)
    ds_meta_data = dsmetadata_service.filter_by_doi(doi)

    if not ds_meta_data:
        abort(404)

    # Get dataset
    dataset = ds_meta_data.data_set

    # Save the cookie to the user's browser
    user_cookie = ds_view_record_service.create_cookie(dataset=dataset)
    resp = make_response(render_template("dataset/view_dataset.html", dataset=dataset))
    resp.set_cookie("view_cookie", user_cookie)

    return resp


@dataset_bp.route("/dataset/unsynchronized/<int:dataset_id>/", methods=["GET"])
@login_required
def get_unsynchronized_dataset(dataset_id):

    # Get dataset
    dataset = dataset_service.get_unsynchronized_dataset(current_user.id, dataset_id)

    if not dataset:
        abort(404)

    return render_template("dataset/view_dataset.html", dataset=dataset)


# feat/4
@dataset_bp.route("/dataset/download_all", methods=["GET"])
def download_all():
    # Validar formato
    format = request.args.get("format")
    valid_formats = ["DIMACS", "GLENCOE", "SPLOT", "UVL"]

    if format not in valid_formats:
        return jsonify({
            "error": "Formato de descarga no soportado",
            "valid_formats": valid_formats
        }), 400

    # Obtener datasets
    datasets = dataset_service.get_all_published_datasets()

    if not datasets:
        return jsonify({
            "error": "No hay datasets disponibles para descargar"
        }), 404

    # Crear directorio temporal
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "all_datasets.zip")

    try:
        with ZipFile(zip_path, "w") as zipf:
            files_added = False
            for dataset in datasets:
                if not dataset.files():
                    continue
                dataset_files_processed = False
                for file in dataset.files():
                    try:
                        file_path = f"uploads/user_{dataset.user_id}/dataset_{dataset.id}/"
                        full_path = os.path.join(file_path, file.name)
                        if not os.path.exists(full_path):
                            logger.warning(f"File not found: {full_path}")
                            continue

                        # Leer y transformar contenido
                        try:
                            if format == "DIMACS":
                                transformed_file_path, original_filename = transform_to_dimacs(file.id)
                                new_filename = f"{original_filename}_cnf.txt"
                            elif format == "GLENCOE":
                                transformed_file_path, original_filename = transform_to_glencoe(file.id)
                                new_filename = f"{original_filename}_glencoe.txt"
                            elif format == "SPLOT":
                                transformed_file_path, original_filename = transform_to_splot(file.id)
                                new_filename = f"{original_filename}_splot.txt"
                            else:  # UVL
                                transformed_file_path = full_path
                                new_filename = file.name

                            with open(transformed_file_path, "r") as transformed_file:
                                content = transformed_file.read()

                            # Añadir al ZIP
                            zip_path = os.path.join(f"dataset_{dataset.id}", new_filename)
                            with zipf.open(zip_path, "w") as zipfile:
                                zipfile.write(content.encode())
                                files_added = True
                                dataset_files_processed = True

                        except Exception as e:
                            logger.error(f"Error processing file {file.name}: {str(e)}")
                            continue

                    except Exception as e:
                        logger.error(f"Error with file in dataset {dataset.id}: {str(e)}")
                        continue

                if not dataset_files_processed:
                    logger.warning(f"No files were processed for dataset {dataset.id}")

            # Si no se añadió ningún archivo, crear un ZIP vacío pero válido
            if not files_added:
                # Añadir un archivo README al ZIP
                with zipf.open("README.txt", "w") as readme:
                    readme.write(b"No files were available for download in the selected format.")

        # Enviar ZIP
        return send_from_directory(
            temp_dir,
            "all_datasets.zip",
            as_attachment=True,
            mimetype="application/zip"
        )

    except Exception as e:
        logger.error(f"Error creating ZIP file: {str(e)}")
        return jsonify({
            "error": "Error al crear el archivo ZIP"
        }), 500

    finally:
        # Limpiar archivos temporales
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except Exception as e:
            logger.error(f"Error cleaning temporary files: {str(e)}")


def transform_to_dimacs(file_id):
    temp_file = tempfile.NamedTemporaryFile(suffix='.dimacs', delete=False)
    try:
        hubfile = HubfileService().get_by_id(file_id)
        fm = UVLReader(hubfile.get_path()).transform()
        sat = FmToPysat(fm).transform()
        DimacsWriter(temp_file.name, sat).transform()

        return temp_file.name, hubfile.name
    finally:
        pass


def transform_to_splot(file_id):
    temp_file = tempfile.NamedTemporaryFile(suffix='.splot', delete=False)
    try:
        hubfile = HubfileService().get_by_id(file_id)
        fm = UVLReader(hubfile.get_path()).transform()

        SPLOTWriter(temp_file.name, fm).transform()

        return temp_file.name, hubfile.name
    finally:
        pass


def transform_to_glencoe(file_id):
    temp_file = tempfile.NamedTemporaryFile(suffix='.glencoe', delete=False)
    try:
        hubfile = HubfileService().get_by_id(file_id)
        fm = UVLReader(hubfile.get_path()).transform()

        GlencoeWriter(temp_file.name, fm).transform()

        return temp_file.name, hubfile.name
    finally:
        pass


@dataset_bp.route("/user/<int:user_id>/datasets")
def user_datasets(user_id):
    user = User.query.get_or_404(user_id)
    datasets = dataset_service.get_datasets_by_user(user_id)
    return render_template(
        "dataset/user_datasets.html",
        datasets=datasets,
        user=user
    )
