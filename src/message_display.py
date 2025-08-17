class UnicodeDisplay:
    def __init__(self):
        self.supports_unicode = self._check_unicode_support()
        self.symbols = self._get_symbols()
    
    def _check_unicode_support(self):
        try:
            "✅❌📚".encode('utf-8')
            return True
        except UnicodeEncodeError:
            return False
    
    def _get_symbols(self):
        if self.supports_unicode:
            return {
                'success': '✅',
                'error': '❌',
                'warning': '⚠️',
                'info': '💡',
                'book': '📚',
                'search': '🔍'
            }
        else:
            return {
                'success': '[OK]',
                'error': '[ERROR]',
                'warning': '[WARN]',
                'info': '[INFO]',
                'book': '[BOOK]',
                'search': '[SEARCH]'
            }
    
    def success(self, message):
        print(f"{self.symbols['success']} {message}")
    
    def error(self, message):
        print(f"{self.symbols['error']} {message}")

    def warning(self, message):
        print(f"{self.symbols['warning']} {message}")

    def info(self, message):
        print(f"{self.symbols['info']} {message}")

    def book(self, message):
        print(f"{self.symbols['book']} {message}")
        
    def search(self, message):
        print(f"{self.symbols['search']} {message}")


