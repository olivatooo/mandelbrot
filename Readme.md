# Mandelbrot Web Crawler

![Mandelbrot Logo](https://cdn.discordapp.com/attachments/1047871048458190869/1194029059605282967/4HeMCYa.png?ex=65aedd37&is=659c6837&hm=731d9971a16c618333a4e65fa83e55c14a9d083c5bdf6b97313fb8926ffb4e07&)

Mandelbrot is parallel and distributed web crawler designed to find URLs in web pages. Named after the famous mathematical set, this crawler aims to traverse the vast landscape of the internet, collecting URLs.

## Features

- **Data Extraction**: Gets all links from the starting URL and extracts data from them.
- **Concurrency**: Supports concurrent crawling to enhance speed and efficiency.
- **User-Friendly Interface**: Intuitive command-line interface for easy configuration and usage.

## Installation

```bash
# Clone the repository
git clone https://github.com/olivatooo/mandelbrot.git

# Navigate to the project directory
cd mandelbrot

# Install dependencies (if any)
pip install -r requirements.txt
```

## Usage

Run the Mandelbrot web crawler using the following command:

```bash
python mandelbrot.py <target_url> [options]
```

Replace `<target_url>` with the starting URL for the crawler.

## Options

- `--depth` (`-d`): Set the maximum depth to search (default: `MAX_DEPTH`).
- `--threads` (`-t`): Specify the number of threads to use (default: `NUMBER_OF_THREADS`).
- `--delay-to-start-threads` (`-dtt`): Set the delay to start the thread swarm (default: `DELAY_TO_START_THREADS`).
- `--infinite-scrolling` (`-ict`): Define how many times infinite scrolling will be triggered (default: `DELAY_TO_START_THREADS`).
- `--infinite-scrolling-delay` (`-icd`): Set the time to wait between each scroll (default: `DELAY_TO_START_THREADS`).
- `--stay-domain` (`-s`): If `true`, the crawler will stay in the same domain (default: `True`).
- `--verify` (`-v`): If `true`, the crawler will verify if the found URL exists (default: `False`).
- `--benchmark` (`-b`): If `true`, the crawler will benchmark the run (forcefully implies `-v`, default: `False`).


## Contributing

We welcome contributions! Open an issue with your complaints or suggestions on our [GitHub repository](https://github.com/olivatooo/mandelbrot).

## License

See License.md
