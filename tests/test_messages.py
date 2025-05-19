import pytest
from wasenderapi.models import (
    TextMessage,
    ImageUrlMessage,
    VideoUrlMessage,
    DocumentUrlMessage,
    AudioUrlMessage,
    StickerUrlMessage,
    ContactCardMessage,
    LocationPinMessage,
    ContactCardPayload,
    LocationPinPayload
)

class TestMessageTypeGuards:
    def test_recognizes_text_message_correctly(self):
        msg = {"to": "+1", "text": "hello", "messageType": "text"}
        assert msg["messageType"] == "text"
        assert msg["text"] == "hello"

    def test_recognizes_image_url_message_correctly(self):
        msg_with_caption = {
            "to": "+1",
            "messageType": "image",
            "imageUrl": "http://example.com/image.png",
            "text": "caption"
        }
        assert msg_with_caption["messageType"] == "image"
        assert msg_with_caption["imageUrl"] == "http://example.com/image.png"
        assert msg_with_caption["text"] == "caption"

        msg_without_caption = {
            "to": "+1",
            "messageType": "image",
            "imageUrl": "http://example.com/image.jpg"
        }
        assert msg_without_caption["messageType"] == "image"
        assert msg_without_caption["imageUrl"] == "http://example.com/image.jpg"
        assert "text" not in msg_without_caption

    def test_recognizes_video_url_message_correctly(self):
        msg_with_caption = {
            "to": "+1",
            "messageType": "video",
            "videoUrl": "http://example.com/video.mp4",
            "text": "watch this"
        }
        assert msg_with_caption["messageType"] == "video"
        assert msg_with_caption["videoUrl"] == "http://example.com/video.mp4"
        assert msg_with_caption["text"] == "watch this"

        msg_without_caption = {
            "to": "+1",
            "messageType": "video",
            "videoUrl": "http://example.com/video.mov"
        }
        assert msg_without_caption["messageType"] == "video"
        assert msg_without_caption["videoUrl"] == "http://example.com/video.mov"
        assert "text" not in msg_without_caption

    def test_recognizes_document_url_message_correctly(self):
        msg_with_caption = {
            "to": "+1",
            "messageType": "document",
            "documentUrl": "http://example.com/doc.pdf",
            "text": "important doc"
        }
        assert msg_with_caption["messageType"] == "document"
        assert msg_with_caption["documentUrl"] == "http://example.com/doc.pdf"
        assert msg_with_caption["text"] == "important doc"

        msg_without_caption = {
            "to": "+1",
            "messageType": "document",
            "documentUrl": "http://example.com/doc.docx"
        }
        assert msg_without_caption["messageType"] == "document"
        assert msg_without_caption["documentUrl"] == "http://example.com/doc.docx"
        assert "text" not in msg_without_caption

    def test_recognizes_audio_url_message_correctly(self):
        msg_with_text = {
            "to": "+1",
            "messageType": "audio",
            "audioUrl": "http://example.com/audio.mp3",
            "text": "listen"
        }
        assert msg_with_text["messageType"] == "audio"
        assert msg_with_text["audioUrl"] == "http://example.com/audio.mp3"
        assert msg_with_text["text"] == "listen"

        msg_without_text = {
            "to": "+1",
            "messageType": "audio",
            "audioUrl": "http://example.com/audio.ogg"
        }
        assert msg_without_text["messageType"] == "audio"
        assert msg_without_text["audioUrl"] == "http://example.com/audio.ogg"
        assert "text" not in msg_without_text

    def test_recognizes_sticker_url_message_correctly(self):
        msg = {
            "to": "+1",
            "messageType": "sticker",
            "stickerUrl": "http://example.com/sticker.webp"
        }
        assert msg["messageType"] == "sticker"
        assert msg["stickerUrl"] == "http://example.com/sticker.webp"
        assert "text" not in msg

    def test_recognizes_contact_card_message_correctly(self):
        contact_payload = {
            "name": "John Doe",
            "phone": "+1234567890"
        }
        msg_with_caption = {
            "to": "+1",
            "messageType": "contact",
            "contact": contact_payload,
            "text": "John's contact"
        }
        assert msg_with_caption["messageType"] == "contact"
        assert msg_with_caption["contact"] == contact_payload
        assert msg_with_caption["text"] == "John's contact"

        msg_without_caption = {
            "to": "+1",
            "messageType": "contact",
            "contact": contact_payload
        }
        assert msg_without_caption["messageType"] == "contact"
        assert msg_without_caption["contact"] == contact_payload
        assert "text" not in msg_without_caption

    def test_recognizes_location_pin_message_correctly(self):
        location_payload = {
            "latitude": 37.7749,
            "longitude": -122.4194,
            "name": "SF Office",
            "address": "123 Main St"
        }
        msg_with_caption = {
            "to": "+1",
            "messageType": "location",
            "location": location_payload,
            "text": "Meet here"
        }
        assert msg_with_caption["messageType"] == "location"
        assert msg_with_caption["location"] == location_payload
        assert msg_with_caption["text"] == "Meet here"

        msg_without_caption = {
            "to": "+1",
            "messageType": "location",
            "location": {"latitude": "10.0", "longitude": "-20.5"}
        }
        assert msg_without_caption["messageType"] == "location"
        assert msg_without_caption["location"]["latitude"] == "10.0"
        assert msg_without_caption["location"]["longitude"] == "-20.5"
        assert "text" not in msg_without_caption 