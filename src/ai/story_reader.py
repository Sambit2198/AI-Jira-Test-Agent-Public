from pathlib import Path


def read_user_story():
    project_folder = Path(__file__).resolve().parents[2]
    story_file = project_folder / "test-data" / "sample_user_story.txt"

    if not story_file.exists():
        print("Error: User story file not found!")
        return None

    story = story_file.read_text(encoding="utf-8")

    print("\n========== USER STORY ==========\n")
    print(story)
    print("\n================================")

    return story


if __name__ == "__main__":
    read_user_story()