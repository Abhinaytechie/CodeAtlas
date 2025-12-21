try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

try:
    print("Testing DDGS Video Search...")
    with DDGS() as ddgs:
        results = list(ddgs.videos("Striver Graph Series Playlist", max_results=1))
        if results:
            print(f"SUCCESS: Found video: {results[0]['content']}")
        else:
            print("FAILURE: No results found")
except Exception as e:
    print(f"ERROR: {e}")
