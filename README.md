# Using Machine Learning to Understand Loneliness in English Long-term Care Users from Free Text Case Notes

This repository accompanies the 2024 paper titled _Using Machine Learning to Understand Loneliness in English Long-term Care Users from Free Text Case Notes_ by Sam Rickman, Jose-Luis Fernandez, and Juliette Malley. Currently, it is a private repository accessible only to individuals with an access token. It will be made public upon the acceptance of the paper for publication.

## What this repository contains

The paper trains a machine learning model to determine whether free text about users of adult social care indicates that they are lonely or socially isolated. This repository includes the final classification model, which can be run on large volumes of free text to generate such classifications.

## Requirements

The model is reproducible as it is encapsulated in a Docker container. The requirements are:

1. **Docker**: To install Docker, follow the instructions at [Docker's official site](https://docs.docker.com/get-docker/).
2. **API Request Tool**: A method for making API requests, such as [curl](https://curl.se/). The container runs the model on an open port (by default, 8000) on the local host, and you can make API requests to the model from that machine.

## How to Run the Model

1. Clone the repository:
   ```sh
   git clone https://github.com/samrickman/lonelinessmodel.git
   ```
2. Navigate into the directory:
   ```sh
   cd lonelinessmodel
   ```
3. Build the Docker image:
   ```sh
   docker build . -t lonelinessimage
   ```
4. Run the Docker container:
   ```sh
   docker run -d --rm --name lonelinessmodel -p 8000:8000 lonelinessimage
   ```

## How to Use

Step four opens port 8000 on the container to port 8000 on the local machine. If you wish to use a different port on the local machine, replace the command with:

```sh
docker run -d --rm --name lonelinessmodel -p <local-port>:8000 lonelinessimage
```

You can then send API requests to the model using the `upload` route. The parameters the upload method takes are:

1. `file`: **Required**. String (file path). The notes to classify. For an example of the expected format, see [`sample_notes.csv`](./app/sample_notes.csv).
2. `out_file`: **Optional**. String (file path). This is a file in the container where the output is saved. By default, this is `./csv_out/sentence_df.csv`. We recommend piping the results of the API response to a local file instead of using this parameter.
3. `anon_mask_file`: **Optional**. String (file path). If data is pseudonymized, this provides words to replace pseudonymized tokens during pre-processing to aid tokenization.
4. `overwrite`: **Optional**. Boolean. Whether to overwrite data in the container if it has been previously used for classification.

Personally I find this easier to understand when I see the code. If you feel similarly, the function signature for the upload method appears as follows:

```python
def upload(
    file: UploadFile = File(...),
    out_file: str = "./csv_out/sentence_df.csv",
    anon_mask_file: UploadFile = None,
    overwrite: bool = Form(False)
):
```

## Examples

Assuming the app is running on the default port:

1. **Basic Usage**: Upload a file (`app/sample_notes.csv`), generate predictions, and write the output to a local file (`results.json`).

   ```sh
   curl -X 'POST' \
     'http://127.0.0.1:8000/upload' \
     -H 'accept: application/json' \
     -H 'Content-Type: multipart/form-data' \
     -F 'file=@app/sample_notes.csv;type=text/csv' \
     > results.json
   ```

2. **Using a Different Set of Constants**: Replace pseudonymized tokens with a different set of constants (`./app/example_diff_constants.json`).

   ```sh
   curl -X 'POST' \
     'http://127.0.0.1:8000/upload' \
     -H 'accept: application/json' \
     -H 'Content-Type: multipart/form-data' \
     -F 'file=@app/sample_notes.csv;type=text/csv' \
     -F 'anon_mask_file=@app/example_diff_constants.json;type=application/json' \
     > results.json
   ```

3. **Overwriting Data**: Overwrite any data already in the container.

   ```sh
   curl -X 'POST' \
     'http://127.0.0.1:8000/upload' \
     -H 'accept: application/json' \
     -H 'Content-Type: multipart/form-data' \
     -F 'file=@app/sample_notes.csv;type=text/csv' \
     -F 'anon_mask_file=@app/example_diff_constants.json;type=application/json' \
     -F 'overwrite=true' \
     > results.json
   ```

## Debugging

The container should return the appropriate error in most cases, such as "file not found." However, if there is an unexpected error, you may see `Internal Server Error`. In such cases, there should be more detailed output within the container. You can find this by running:

```sh
docker logs lonelinessmodel
```

(assuming your container is named `lonelinessmodel`). If the error is not immediately clear, please raise a GitHub issue.

# LICENSE

This project is licensed under the GNU General Public License v3.0.

The full text of the GNU General Public License can be found in the LICENSE file.

## Attribution

This project builds upon the model ], which is licensed under the GNU General Public License v3.0.

## Additional Licenses

This project also makes use of the following libraries, which are licensed as follows:

- Library1: MIT License
- Library2: BSD License
- Library3: Apache License 2.0

For the full text of these licenses, please refer to the LICENSES.txt file.