from src.stream.manager import StreamManager


class TestStreamManagerEdgeCases:
    def test_empty_sources(self):
        sm = StreamManager(sources={})
        assert len(sm.caps) == 0
        sm.release_all()

    def test_get_frame_nonexistent(self):
        sm = StreamManager(sources={})
        success, frame = sm.get_frame("nonexistent")
        assert success is False
        assert frame is None
        sm.release_all()

    def test_reconnect_schedules_only_once(self):
        import time

        sm = StreamManager(sources={})
        sm.sources["test"] = 999
        sm._schedule_reconnect("test")
        assert sm._reconnecting.get("test") is True
        sm._schedule_reconnect("test")
        assert sm._reconnecting.get("test") is True
        time.sleep(1)
        sm.release_all()
