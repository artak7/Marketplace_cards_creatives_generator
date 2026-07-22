import streamlit as st
from io import BytesIO
from config import Config
from services.ai_service import AIService
from services.image_service import ImageService
from services.s3_service import S3Service
from services.wb_service import WildberriesService

# Instantiate services
ai_service = AIService(Config.GROQ_API_KEY)
s3_service = S3Service(
    key_id=Config.S3_ACCESS_KEY_ID,
    secret_key=Config.S3_SECRET_ACCESS_KEY,
    endpoint=Config.S3_ENDPOINT_URL,
    bucket_name=Config.S3_BUCKET_NAME
)

# Page setups
st.set_page_config(page_title="Генератор карточек одежды", layout="wide")
st.title("🎨 Генератор карточек одежды для WB")
# st.caption("Рефакторинг на основе SOLID / DRY / KISS")

# State setups
for key, default in [
    ("clean_mockup", None), ("current_prompt", ""), ("wb_title", ""), 
    ("wb_description", ""), ("b1_text", "100% ХЛОПОК"), ("b2_text", "OVERSIZE КРОЙ")
]:
    if key not in st.session_state:
        st.session_state[key] = default

# 🤖 STEP 1: SEO Generator (Groq)
if st.button("🤖 Придумать идею и SEO-текст (Groq)"):
    if not Config.GROQ_API_KEY:
        st.error("Пожалуйста, настройте GROQ_API_KEY в .env файле.")
    else:
        with st.spinner("Генерируем креативы в Groq..."):
            try:
                data = ai_service.generate_seo_content()
                st.session_state.current_prompt = data.get("prompt", "")
                st.session_state.wb_title = data.get("title", "")
                st.session_state.wb_description = data.get("description", "")
                st.success("Идея и SEO-тексты успешно созданы!")
            except Exception as e:
                st.error(f"Ошибка Groq: {e}")

# 📝 STEP 2: Content Tuning
st.subheader("📝 Настройка контента карточки")
user_title = st.text_input("Название товара для WB:", value=st.session_state.wb_title)
user_description = st.text_area("SEO-описание товара:", value=st.session_state.wb_description, height=120)
user_prompt = st.text_area("Промпт для генерации принта (Pollinations):", value=st.session_state.current_prompt, height=80)

# 🎨 STEP 3: Badge Adjustments
with st.expander("🎨 Настройка инфографики"):
    color_options = list(Config.COLOR_MAP.keys())
    
    col1, col2 = st.columns(2)
    with col1:
        b1_enabled = st.checkbox("Включить первую плашку", value=True)
        b1_text = st.text_input("Текст первой:", value=st.session_state.b1_text)
        b1_color = st.selectbox("Цвет первой:", color_options, index=0)
    with col2:
        b2_enabled = st.checkbox("Включить вторую плашку", value=True)
        b2_text = st.text_input("Текст второй:", value=st.session_state.b2_text)
        b2_color = st.selectbox("Цвет второй:", color_options, index=1)

# 🚀 STEP 4: Render
if st.button("🚀 Создать принт и карточку"):
    if not user_prompt.strip():
        st.warning("Промпт не должен быть пустым.")
    else:
        with st.spinner("Создаём шедевр..."):
            try:
                # 1. Image generation
                print_img = ai_service.generate_print_image(user_prompt)
                
                # 2. Mockup composition
                mockup = ImageService.create_mockup("tshirt_base_grey.png", print_img)
                st.session_state.clean_mockup = mockup
                
                # 3. Apply infographic labels
                badges = [
                    {"enabled": b1_enabled, "text": b1_text, "color": Config.COLOR_MAP[b1_color]},
                    {"enabled": b2_enabled, "text": b2_text, "color": Config.COLOR_MAP[b2_color]}
                ]
                final_card = ImageService.apply_infographics(mockup, badges)
                st.session_state.final_card = final_card
                
                # Render results in columns
                c1, c2 = st.columns(2)
                with c1:
                    st.image(print_img, caption="Сгенерированный принт", use_container_width=True)
                with c2:
                    st.image(final_card, caption="Финальная карточка", use_container_width=True)
                    
            except Exception as e:
                st.error(f"Ошибка при генерации: {e}")

# 📤 STEP 5: Wildberries Uploads & Downloads
if "final_card" in st.session_state and st.session_state.final_card:
    st.markdown("---")
    st.subheader("📦 Автоматическая выгрузка на Wildberries")
    
    # Защита: проверяем, инициализирован ли s3_service
    # Если s3_service — это None или не настроен, кнопка должна быть заблокирована
    s3_ready = s3_service is not None
    
    wb_token = st.text_input("Введите ваш токен WB API:", type="password")
    vendor_code = st.text_input("Артикул товара (Vendor Code):", value="tshirt_ai_001")
    
    # Две новые переменные, которых не было в локальном scope шага 5:
    # Убедитесь, что user_title и user_description объявлены выше в вашем коде
    user_title = st.session_state.get("wb_title", "Название товара")
    user_description = st.session_state.get("wb_description", "Описание товара")
    
    if st.button("📤 Создать карточку и загрузить на WB", disabled=not s3_ready):
        if not wb_token:
            st.warning("Пожалуйста, укажите токен ВБ API.")
        else:
            # Создается пустое черное текстовое окошко на экране
            log_container = st.code("Система запущена...\n", language="text")
            st.session_state["debug_logs"] = "" # Сброс логов

            def add_log(text: str, container=log_container):
                """Берет старый текст, добавляет к нему новую строчку и обновляет окошко на экране"""
                st.session_state["debug_logs"] = st.session_state.get("debug_logs", "") + text + "\n"
                container.code(st.session_state["debug_logs"], language="text")

            with st.spinner("Загрузка в облако и создание карточки WB..."):
                try:
                    # 1. Загрузка в приватный S3 (получаем подписанную ссылку)
                    filename = f"{vendor_code}.jpg"
                    img_url = s3_service.upload_image(st.session_state.final_card, filename)
                    
                    # 2. Создание карточки товара
                    created, wb_response_text = WildberriesService.create_card(wb_token, vendor_code, user_title, user_description)
                    
                    add_log(f"Ответ от ВБ движком curl_cffi:\n{wb_response_text}")

                    if created:
                        st.info("Номенклатура создается на серверах WB (это занимает до 1-2 минут)...")
                        
                        # 3. Передаем в link_media ссылку. 
                        # Внутри link_media ВАЖНО сделать паузу/запрос nmId по vendor_code!
                        linked = WildberriesService.link_media(wb_token, vendor_code, img_url)
                        
                        if linked:
                            st.success(f"🎉 Карточка {vendor_code} успешно выгружена на WB с фото!")
                        else:
                            st.warning(
                                f"Товар создан! Но WB еще обрабатывает карточку. "
                                f"Вы можете загрузить фото вручную по этой ссылке (действует 7 дней):\n\n"
                                f"`{img_url}`"
                            )
                    else:
                        st.error("Ошибка при создании карточки в Wildberries API. Проверьте токен и формат данных.")
                except Exception as e:
                    st.error(f"Ошибка экспорта: {e}")
    
    if not s3_ready:
        st.error("⚠️ S3 Сервис не настроен. Проверьте переменные окружения в .env файле.")


    # Local file download alternative
    buffered = BytesIO()
    st.session_state.final_card.convert("RGB").save(buffered, format="JPEG", quality=95)
    st.download_button(
        label="📥 Скачать готовую карточку на ПК",
        data=buffered.getvalue(),
        file_name=f"{vendor_code}.jpg",
        mime="image/jpeg"
    )