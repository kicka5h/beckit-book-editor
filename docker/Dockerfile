FROM python:3.11-slim

# System dependencies: git (for GitPython), pandoc + TeX (for PDF export)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    pandoc \
    texlive-latex-base \
    texlive-latex-recommended \
    texlive-fonts-recommended \
    texlive-latex-extra \
    lmodern \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (cached layer)
COPY pyproject.toml ./
COPY src/ src/
RUN pip install --upgrade pip && pip install -e ".[dev]"

# Copy remaining source (tests, config files, etc.)
COPY . .

ENV BECKIT_WEB=1
EXPOSE 8080

CMD ["python", "-m", "book_editor"]
