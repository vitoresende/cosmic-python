import tempfile
from pathlib import Path
import shutil
from sync import sync, determine_actions


class TestE2E:
    @staticmethod
    def test_when_a_file_exists_in_the_source_but_not_the_destination():
        try:
            source = tempfile.mkdtemp()
            dest = tempfile.mkdtemp()

            content = "I am a very useful file"
            (Path(source) / "my-file").write_text(content)

            sync(source, dest)

            expected_path = Path(dest) / "my-file"
            assert expected_path.exists()
            assert expected_path.read_text() == content

        finally:
            shutil.rmtree(source)
            shutil.rmtree(dest)

    @staticmethod
    def test_when_a_file_has_been_renamed_in_the_source():
        try:
            source = tempfile.mkdtemp()
            dest = tempfile.mkdtemp()

            content = "I am a file that was renamed"
            source_path = Path(source) / "source-filename"
            old_dest_path = Path(dest) / "dest-filename"
            expected_dest_path = Path(dest) / "source-filename"
            source_path.write_text(content)
            old_dest_path.write_text(content)

            sync(source, dest)

            assert old_dest_path.exists() is False
            assert expected_dest_path.read_text() == content

        finally:
            shutil.rmtree(source)
            shutil.rmtree(dest)
    
    @staticmethod
    def test_when_a_file_exists_in_the_destination_but_not_the_source():
        # This tests the deletion functionality.
        try:
            source = tempfile.mkdtemp()
            dest = tempfile.mkdtemp()

            content = "I am a file that should be deleted"
            dest_path = Path(dest) / "file-to-delete"
            dest_path.write_text(content)

            sync(source, dest)

            assert not dest_path.exists()

        finally:
            shutil.rmtree(source)
            shutil.rmtree(dest)

    @staticmethod
    def test_when_source_and_destination_have_identical_files():
        # This ensures no unnecessary actions are taken when the directories are already in sync.
        try:
            source = tempfile.mkdtemp()
            dest = tempfile.mkdtemp()

            content = "I am a file that exists in both directories"
            source_path = Path(source) / "identical-file"
            dest_path = Path(dest) / "identical-file"
            source_path.write_text(content)
            dest_path.write_text(content)

            sync(source, dest)

            assert dest_path.exists()
            assert dest_path.read_text() == content

        finally:
            shutil.rmtree(source)
            shutil.rmtree(dest)
    
    @staticmethod
    def test_when_source_has_multiple_files_and_destination_is_empty():
        # This ensures all files are copied over correctly.
        try:
            source = tempfile.mkdtemp()
            dest = tempfile.mkdtemp()

            files_content = {
                "file1": "Content of file 1",
                "file2": "Content of file 2",
                "file3": "Content of file 3"
            }

            for filename, content in files_content.items():
                (Path(source) / filename).write_text(content)

            sync(source, dest)

            for filename, content in files_content.items():
                expected_path = Path(dest) / filename
                assert expected_path.exists()
                assert expected_path.read_text() == content

        finally:
            shutil.rmtree(source)
            shutil.rmtree(dest)

    @staticmethod
    def test_when_a_file_is_renamed_and_another_new_file_is_added():
        # This ensures both renaming and copying new files work together correctly.
        try:
            source = tempfile.mkdtemp()
            dest = tempfile.mkdtemp()

            renamed_content = "This file was renamed"
            new_file_content = "This is a new file"

            source_renamed_path = Path(source) / "new-filename"
            dest_old_path = Path(dest) / "old-filename"
            source_new_path = Path(source) / "new-file"

            source_renamed_path.write_text(renamed_content)
            dest_old_path.write_text(renamed_content)
            source_new_path.write_text(new_file_content)

            sync(source, dest)

            assert not dest_old_path.exists()
            assert (Path(dest) / "new-filename").read_text() == renamed_content
            assert (Path(dest) / "new-file").read_text() == new_file_content

        finally:
            shutil.rmtree(source)
            shutil.rmtree(dest)



def test_when_a_file_exists_in_the_source_but_not_the_destination():
    source_hashes = {"hash1": "fn1"}
    dest_hashes = {}
    actions = determine_actions(source_hashes, dest_hashes, Path("/src"), Path("/dst"))
    assert list(actions) == [("COPY", Path("/src/fn1"), Path("/dst/fn1"))]


def test_when_a_file_has_been_renamed_in_the_source():
    source_hashes = {"hash1": "fn1"}
    dest_hashes = {"hash1": "fn2"}
    actions = determine_actions(source_hashes, dest_hashes, Path("/src"), Path("/dst"))
    assert list(actions) == [("MOVE", Path("/dst/fn2"), Path("/dst/fn1"))]