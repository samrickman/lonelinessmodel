[![DOI](https://zenodo.org/badge/825260712.svg)](https://doi.org/10.5281/zenodo.13934375)

# Understanding patterns of loneliness in older long-term care users using natural language processing with free text case notes

This repository relates to the 2024 work, _Using Machine Learning to Understand Loneliness in English Long-term Care Users from Free Text Case Notes_ by Sam Rickman, Jose-Luis Fernandez, and Juliette Malley. It will be updated with a link to the paper upon publication.

## Abstract of the work

Loneliness and social isolation are distressing for individuals and a predictor of mortality. Evidence about the impact of loneliness and isolation on publicly funded long-term care usage is limited as there is little data indicating whether individuals using care services are lonely or socially isolated. Recent developments in natural language processing have made it possible to extract information from electronic care records, which contain large quantities of free text notes. We identify loneliness or social isolation from free text by analysing pseudonymised administrative care records containing 1.1m free text case notes about 3,046 older adults recorded in a London council between November 2008 and August 2020. We use three natural language processing methods to represent the labelled notes as vectors: document-term matrices, word embeddings and transformers. The most accurate model used a bidirectional transformers architecture. Evaluated on a test set of unseen sentences this model had an $F_1$ score of 0.92. We generate predictions of loneliness or isolation on the rest of the data using the best-performing model to examine the construct validity of our indicator by comparing it with other datasets and the literature. Our measure generally behaves as we expect: it is highly correlated with living alone, which we see in survey data. It is also associated with impaired memory which we expect from the literature. Furthermore, our indicator of loneliness or social isolation is a strong predictor of whether an individual receives services for social inclusion. According to our model, around 43% of individuals have a sentence indicating loneliness or social isolation in their case notes at the time of their initial care assessment. Similar estimates of prevalence are obtainable from individual-level survey data. The advantage of our method over surveys is that classified free text administrative data can be used in conjunction with other data in administrative records, such as care expenditure or service use. The outputs of our model can be used to generate inputs for regression models of service use which include social isolation and loneliness as a dependent variable. The paper is accommanied by an open-source model of the work, which is contained within [this](https://github.com/samrickman/lonelinessmodel) GitHub repo.

# What this repository contains

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

Step four opens port 8000 on the container to port 8000 on the local machine. If you wish to use a different port on the local machine, replace the command with:

```sh
docker run -d --rm --name lonelinessmodel -p <local-port>:8000 lonelinessimage
```

## How to Use

You can send API requests to the model by uploading a file to be classified to the `upload` endpoint. The parameters the upload route takes are:

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

This project builds upon several works licensed under the GNU General Public License v3.0, so is therefore also licensed under GPL.

The full text of the GNU General Public License can be found in the LICENSE file.

This project also makes use of the several libraries licensed under the MIT, BSD and Apache License 2.0. For the full text of these licenses and which software they refer to, please refer to the [`LICENSE`](./LICENSE) file.

# Citation

If you use this code in your research, please cite:

Rickman, S. (2024). _Understanding patterns of loneliness in older long-term care users using natural language processing with free text case notes_ (v1.0.0). Zenodo. [https://doi.org/10.5281/zenodo.13934375](https://doi.org/10.5281/zenodo.13934375)