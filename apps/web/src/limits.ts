// API ile aynı olması gereken sabitler. Kaynakları parantez içinde; testler eşitliği denetler
// (tests/test_web_limits.py).

/** En uzun soru (src/visual_agent/domain/conversation.py: MAX_QUESTION_CHARS). */
export const MAX_QUESTION_CHARS = 2000;

/** En büyük yükleme (apps/api/main.py: MAX_UPLOAD_BYTES; nginx client_max_body_size). */
export const MAX_UPLOAD_BYTES = 100 * 1024 * 1024;

/** Yüklenebilen uzantılar (src/visual_agent/ingest/formats.py: _TYPES). */
export const ACCEPTED_TYPES =
  ".pdf,.docx,.doc,.pptx,.ppt,.odt,.rtf,.xlsx,.xls,.jpg,.jpeg,.png,.tif,.tiff,.sql,.txt,.md";

export function uploadLimitMessage(): string {
  return `Dosya ${MAX_UPLOAD_BYTES / (1024 * 1024)} MB sınırını aşıyor.`;
}
