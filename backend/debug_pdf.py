
import io
import sys

try:
    import pypdf
    print(f"pypdf version: {pypdf.__version__}")
except ImportError:
    print("pypdf not installed")
    sys.exit(1)

from pypdf import PdfReader

def test_pdf():
    # Create a minimal PDF in memory for testing
    # This is a bit complex to raw-byte, so we'll just test the import and checking a string fails gracefully
    try:
        dummy_stream = io.BytesIO(b"not a pdf")
        reader = PdfReader(dummy_stream)
        print("Reader initialized (unexpected success on garbage)")
    except Exception as e:
        print(f"Caught expected error or other error: {e}")

if __name__ == "__main__":
    test_pdf()
