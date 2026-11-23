"""Hinglish translation engine using LLM APIs."""
import os
import json
import asyncio
from typing import List, Dict, Any
import openai
import google.generativeai as genai
from app.config import get_settings

settings = get_settings()

HINGLISH_SYSTEM_PROMPT = """You are a Hinglish translation expert. Convert the given English/Hindi text into natural, conversational Hinglish.

CRITICAL RULES:
1. NEVER produce pure Hindi. Always mix Hindi and English naturally.
2. Preserve technical terms, brand names, and proper nouns in English.
3. Maintain the original tone, emotion, jokes, and informality.
4. Use "hai", "hoga", "kar raha hai" etc. naturally.
5. Keep sentence structure conversational, not formal.
6. If the input is already Hinglish, improve it if needed but preserve meaning.

Examples:
- "Artificial intelligence is transforming industries." → "Artificial intelligence industries ko transform kar raha hai."
- "I need to submit the assignment tomorrow." → "Mujhe assignment kal submit karna hai."
- "The meeting was very productive." → "Meeting bahut productive thi."
- "Let's grab some coffee." → "Chalo coffee peete hain."
- "The API response time is too slow." → "API response time bahut slow hai."

Output ONLY the translated text. No explanations, no quotes around output."""

class TranslationService:
    def __init__(self):
        self.provider = "gemini" if settings.GEMINI_API_KEY else "openai"
        if self.provider == "gemini":
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            openai.api_key = settings.OPENAI_API_KEY

    async def translate_segment(self, text: str, context: str = "") -> str:
        """Translate a single text segment to Hinglish."""
        prompt = f"Context: {context}\n\nTranslate to Hinglish: {text}"

        if self.provider == "gemini":
            return await self._translate_gemini(prompt)
        else:
            return await self._translate_openai(prompt)

    async def _translate_gemini(self, prompt: str) -> str:
        try:
            response = await asyncio.to_thread(
                self.gemini_model.generate_content,
                [
                    {"role": "user", "parts": [HINGLISH_SYSTEM_PROMPT]},
                    {"role": "model", "parts": ["Understood. I will translate to natural Hinglish following all rules."]},
                    {"role": "user", "parts": [prompt]}
                ],
                generation_config={"temperature": 0.3, "max_output_tokens": 512}
            )
            return response.text.strip()
        except Exception as e:
            print(f"Gemini translation error: {e}")
            return text  # Fallback

    async def _translate_openai(self, prompt: str) -> str:
        try:
            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": HINGLISH_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=512
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI translation error: {e}")
            return text

    async def translate_segments(self, segments: List[Dict], batch_size: int = 5) -> List[Dict]:
        """Translate multiple segments with context awareness."""
        translated = []
        context_window = []

        for i, seg in enumerate(segments):
            context = " ".join([s["text"] for s in context_window[-3:]])
            translated_text = await self.translate_segment(seg["text"], context)

            seg["translated_text"] = translated_text
            translated.append(seg)
            context_window.append(seg)

            # Small delay to respect rate limits
            if (i + 1) % batch_size == 0:
                await asyncio.sleep(0.5)

        return translated

    async def translate_live(self, text: str, speaker: str = "") -> str:
        """Fast translation for live streaming."""
        prompt = f"Speaker: {speaker}\nText: {text}"

        if self.provider == "gemini":
            try:
                response = await asyncio.to_thread(
                    self.gemini_model.generate_content,
                    prompt,
                    generation_config={"temperature": 0.2, "max_output_tokens": 256}
                )
                return response.text.strip()
            except:
                return text
        else:
            try:
                response = await asyncio.to_thread(
                    openai.ChatCompletion.create,
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": HINGLISH_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=256
                )
                return response.choices[0].message.content.strip()
            except:
                return text
