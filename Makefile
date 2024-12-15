reqs:
	uv pip install -r requirements.txt
	@echo "Requirements installed"

run:
	streamlit run app.py
	@echo "App running"
