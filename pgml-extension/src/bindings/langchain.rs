use anyhow::Result;
use once_cell::sync::Lazy;
use pgrx::*;
use pyo3::prelude::*;
use pyo3::types::PyTuple;

use crate::{bindings::TracebackError, create_pymodule};

create_pymodule!("/src/bindings/langchain.py");

pub fn chunk(splitter: &str, text: &str, kwargs: &serde_json::Value) -> Result<Vec<String>> {
    crate::bindings::venv::activate()?;

    let kwargs = serde_json::to_string(kwargs).unwrap();

    Python::with_gil(|py| -> Result<Vec<String>> {
        let chunk: Py<PyAny> = get_module!(PY_MODULE).getattr(py, "chunk")?;

        Ok(chunk
            .call1(
                py,
                PyTuple::new(
                    py,
                    &[splitter.into_py(py), text.into_py(py), kwargs.into_py(py)],
                ),
            )?
            .extract(py)?)
    })
}
