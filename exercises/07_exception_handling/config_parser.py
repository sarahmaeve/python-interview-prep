class ConfigParser:
    """A simple configuration parser with defaults support."""

    def __init__(self, defaults=None):
        self._defaults = defaults if defaults is not None else {}
        self._config = {}

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def get_config(self):
        """Return a copy of the current configuration dictionary."""
        return dict(self._config)

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def load_config(self, config_dict):
        """Merge *config_dict* into the internal config.

        Any keys present in *defaults* but missing from *config_dict* are
        filled in automatically.
        """
        # BUG 1: bare except catches KeyboardInterrupt and SystemExit
        try:
            for key, value in config_dict.items():
                self._config[key] = value
        except:
            pass

        # Apply defaults for any missing keys
        for key, value in self._defaults.items():
            if key not in self._config:
                self._config[key] = value

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def get(self, key):
        """Return the value for *key*, or raise ``KeyError``."""
        return self._config[key]

    def get_int(self, key):
        """Return the value for *key* converted to ``int``.

        Raises ``ValueError`` with a descriptive message when conversion
        fails.
        """
        value = self.get(key)
        # BUG 2: re-raises as generic Exception with empty message
        try:
            return int(value)
        except ValueError:
            raise Exception("")

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self, required_keys):
        """Raise ``ValueError`` listing every key in *required_keys* that
        is missing from the current config.

        Raises ``TypeError`` if *required_keys* is not iterable (e.g. None).
        """
        # BUG 3: silently swallows TypeError when required_keys is None
        try:
            missing = [k for k in required_keys if k not in self._config]
        except TypeError:
            return

        if missing:
            raise ValueError(
                f"Missing required config keys: {', '.join(missing)}"
            )
