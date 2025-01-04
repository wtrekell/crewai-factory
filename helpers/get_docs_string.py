import os
import sys
import time
import uuid

from crewai.knowledge.source.base_knowledge_source import BaseKnowledgeSource
from pydantic import BaseModel, Field
from typing import Dict, Any


def get_combined_mdx_content(directory="docs_crewai"):
    mdx_contents = []
    spinner = ["|", "/", "-", "\\"]
    idx = 0
    sys.stdout.write("Reading .mdx files ")
    sys.stdout.flush()
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(".mdx"):
                    # Update spinner
                    sys.stdout.write("\b" + spinner[idx % len(spinner)])
                    sys.stdout.flush()
                    idx += 1
                    time.sleep(0.05)
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                            mdx_contents.append(f.read())
                    except Exception as e:
                        # Handle any file reading errors
                        sys.stderr.write(f"\nError reading {file_path}: {str(e)}\n")
        sys.stdout.write("\bDone!\n")
    except Exception as e:
        sys.stdout.write("\n")
        sys.stderr.write(f"Error walking through directory '{directory}': {str(e)}\n")
    return "\n".join(mdx_contents)


def get_combined_content_from_txt(file_path="docs_crewai/singlefile.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")
    except Exception as e:
        raise Exception(f"Error reading file '{file_path}': {e}")

class LocalTxTFileKnowledgeSource(BaseKnowledgeSource):
    file_path: str = Field(description="Path to the local .txt file")
    def load_content(self) -> Dict[str, str]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                content = file.read()

            return {self.file_path: content}
        except Exception as e:
            raise ValueError(f"Failed to read the file {self.file_path}: {str(e)}")

    def add(self) -> None:
        content = self.load_content()
        # print(content)
        for _, text in content.items():
            chunks = self._chunk_text(text)
            self.chunks.extend(chunks)

            chunks_metadata = [
                {
                    "chunk_id": str(uuid.uuid4()),
                    "source": self.file_path,
                    "description": f"Chunk {i + 1} from file {self.file_path}"
                }
                for i in range(len(chunks))
            ]

        self.save_documents(metadata=chunks_metadata)