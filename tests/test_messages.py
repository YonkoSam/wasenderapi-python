import pytest
from wasenderapi.models import (
    TextMessage,
    ImageMessage,
    VideoMessage,
    DocumentMessage,
    AudioMessage,
    StickerMessage,
    ContactMessage,
    LocationMessage,
    ContactCard,
    LocationPin
)
from pydantic import ValidationError

class TestMessageModels:
    def test_text_message_model(self):
        # Valid model
        data = {"to": "+12345", "text": "hello world"}
        model = TextMessage(**data)
        assert model.to == data["to"]
        assert model.text == data["text"]
        assert model.message_type == "text"
        expected_payload = {"to": data["to"], "messageType": "text", "text": data["text"]}
        assert model.model_dump(by_alias=True) == expected_payload
        with pytest.raises(ValidationError):
            TextMessage(to="+12345") # Missing 'text'

    def test_image_message_model(self):
        # With caption
        data_caption = {"to": "+1", "imageUrl": "http://img.png", "text": "caption"}
        model_caption = ImageMessage(**data_caption)
        assert model_caption.to == "+1"
        assert model_caption.image_url == "http://img.png"
        assert model_caption.text == "caption"
        assert model_caption.model_dump(by_alias=True, exclude_none=True) == {
            "to": "+1",
            "messageType": "image",
            "imageUrl": "http://img.png",
            "text": "caption",
        }

        # Without caption
        data_no_caption = {"to": "+1", "imageUrl": "http://img.org"}
        model_no_caption = ImageMessage(**data_no_caption)
        assert model_no_caption.text is None
        assert model_no_caption.model_dump(by_alias=True, exclude_none=True) == {
            "to": "+1",
            "messageType": "image",
            "imageUrl": "http://img.org",
        }
        with pytest.raises(ValidationError):
            ImageMessage(to="+1")

    def test_video_message_model(self):
        # With caption
        data_caption = {"to": "+1", "videoUrl": "http://vid.mp4", "text": "watch"}
        model_caption = VideoMessage(**data_caption)
        assert model_caption.to == "+1"
        assert model_caption.video_url == "http://vid.mp4"
        assert model_caption.text == "watch"
        assert model_caption.model_dump(by_alias=True, exclude_none=True) == {
            "to": "+1",
            "messageType": "video",
            "videoUrl": "http://vid.mp4",
            "text": "watch",
        }

        # Without caption
        data_no_caption = {"to": "+1", "videoUrl": "http://vid.org"}
        model_no_caption = VideoMessage(**data_no_caption)
        assert model_no_caption.text is None
        assert model_no_caption.model_dump(by_alias=True, exclude_none=True) == {
            "to": "+1",
            "messageType": "video",
            "videoUrl": "http://vid.org",
        }
        with pytest.raises(ValidationError):
            VideoMessage(to="+1") # videoUrl is required

    def test_document_message_model(self):
        # With caption
        data_caption = {"to": "+1", "documentUrl": "http://doc.pdf", "text": "doc"}
        model_caption = DocumentMessage(**data_caption)
        assert model_caption.to == "+1"
        assert model_caption.document_url == "http://doc.pdf"
        assert model_caption.text == "doc"
        assert model_caption.model_dump(by_alias=True, exclude_none=True) == {
            "to": "+1",
            "messageType": "document",
            "documentUrl": "http://doc.pdf",
            "text": "doc",
        }

        # Without caption
        data_no_caption = {"to": "+1", "documentUrl": "http://doc.org"}
        model_no_caption = DocumentMessage(**data_no_caption)
        assert model_no_caption.text is None
        assert model_no_caption.model_dump(by_alias=True, exclude_none=True) == {
            "to": "+1",
            "messageType": "document",
            "documentUrl": "http://doc.org",
        }
        with pytest.raises(ValidationError):
            DocumentMessage(to="+1") # documentUrl is required

    def test_audio_message_model(self):
        # AudioUrlMessage has optional text (caption-like) and no ptt field in model itself.
        # The ptt is handled by client helper logic, not a model field.
        data_with_text = {"to": "+1", "audioUrl": "http://audio.mp3", "text": "listen"}
        model_with_text = AudioMessage(**data_with_text)
        assert model_with_text.to == "+1"
        assert model_with_text.audio_url == "http://audio.mp3"
        assert model_with_text.text == "listen"
        assert model_with_text.model_dump(by_alias=True, exclude_none=True) == {
            "to": "+1",
            "messageType": "audio",
            "audioUrl": "http://audio.mp3",
            "text": "listen",
        }

        # Without text
        data_no_text = {"to": "+1", "audioUrl": "http://audio.ogg"}
        model_no_text = AudioMessage(**data_no_text)
        assert model_no_text.to == "+1"
        assert model_no_text.audio_url == "http://audio.ogg"
        assert model_no_text.text is None
        assert model_no_text.model_dump(by_alias=True, exclude_none=True) == {
            "to": "+1",
            "messageType": "audio",
            "audioUrl": "http://audio.ogg",
        }

        with pytest.raises(ValidationError):
            AudioMessage(to="+1")  # audioUrl is required

    def test_sticker_message_model(self):
        # StickerUrlMessage has sticker_url and text is explicitly None in model definition.
        data = {"to": "+1", "stickerUrl": "http://sticker.webp"}
        model = StickerMessage(**data)
        assert model.to == "+1"
        assert model.sticker_url == "http://sticker.webp"
        assert model.text is None # StickerUrlMessage defines `text: None = None`
        
        # Test serialization
        assert model.model_dump(by_alias=True, exclude_none=True) == {
            "to": "+1",
            "messageType": "sticker",
            "stickerUrl": "http://sticker.webp",
        }
        # Test serialization when text is explicitly None (should still be excluded by exclude_none=True)
        assert model.model_dump(by_alias=True) == {
            "to": "+1",
            "messageType": "sticker",
            "stickerUrl": "http://sticker.webp",
            "text": None, # StickerMessage.text is None by definition
        }

        # Test validation: stickerUrl is required
        with pytest.raises(ValidationError):
            StickerMessage(to="+1")

        # Test validation: providing a non-None text should fail because StickerUrlMessage.text is typed as None
        with pytest.raises(ValidationError):
            StickerMessage(to="+1", stickerUrl="http://sticker.webp", text="some text")

    def test_contact_message_model(self):
        contact_data = {"name": "John Doe", "phone": "+1234567890"}
        # With caption (text field on ContactCardMessage)
        data_caption = {"to": "+1", "contact": contact_data, "text": "John contact"}
        model_caption = ContactMessage(**data_caption)
        assert model_caption.contact.name == contact_data["name"]
        assert model_caption.contact.phone == contact_data["phone"]
        assert model_caption.text == data_caption["text"]
        expected_payload_caption = {"to": "+1", "messageType": "contact", "contact": contact_data, "text": "John contact"}
        assert model_caption.model_dump(by_alias=True) == expected_payload_caption

        # Without caption
        data_no_caption = {"to": "+1", "contact": contact_data}
        model_no_caption = ContactMessage(**data_no_caption)
        assert model_no_caption.contact.name == contact_data["name"]
        assert model_no_caption.text is None
        dumped_no_caption = model_no_caption.model_dump(by_alias=True, exclude_none=True)
        assert "text" not in dumped_no_caption
        with pytest.raises(ValidationError):
            ContactMessage(to="+1") # Missing 'contact'
        with pytest.raises(ValidationError):
            ContactMessage(to="+1", contact={}) # Missing contact fields

    def test_location_message_model(self):
        location_data = {"latitude": 37.7749, "longitude": -122.4194, "name": "SF Office", "address": "123 Main St"}
        # With caption (text field on LocationPinMessage)
        data_caption = {"to": "+1", "location": location_data, "text": "Meet here"}
        model_caption = LocationMessage(**data_caption)
        assert model_caption.location.latitude == location_data["latitude"]
        assert model_caption.location.name == location_data["name"]
        assert model_caption.text == data_caption["text"]
        expected_payload_caption = {"to": "+1", "messageType": "location", "location": location_data, "text": "Meet here"}
        assert model_caption.model_dump(by_alias=True) == expected_payload_caption

        # Without caption, and string lat/lon (model supports Union[float, str])
        location_data_str = {"latitude": "10.0", "longitude": "-20.5"}
        data_no_caption = {"to": "+1", "location": location_data_str}
        model_no_caption = LocationMessage(**data_no_caption)
        assert model_no_caption.location.latitude == "10.0"
        assert model_no_caption.location.longitude == "-20.5"
        assert model_no_caption.text is None
        dumped_no_caption = model_no_caption.model_dump(by_alias=True, exclude_none=True)
        assert "text" not in dumped_no_caption 
        # Ensure string lat/lon are preserved in dump if that's intended
        assert dumped_no_caption["location"]["latitude"] == "10.0" 

        with pytest.raises(ValidationError):
            LocationMessage(to="+1") # Missing 'location'
        with pytest.raises(ValidationError):
            LocationMessage(to="+1", location={}) # Missing location fields latitude/longitude 