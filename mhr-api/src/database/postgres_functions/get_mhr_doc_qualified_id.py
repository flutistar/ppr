"""Maintain db function get_mhr_doc_qualified_id here."""
from alembic_utils.pg_function import PGFunction


get_mhr_doc_qualified_id = PGFunction(
  schema="public",
  signature="get_mhr_doc_qualified_id()",
  definition=r"""
  RETURNS VARCHAR
  LANGUAGE plpgsql
  AS
  $$
    BEGIN
        RETURN trim(to_char(nextval('mhr_doc_id_qualified_seq'), '00000000'));
    END
  ; 
  $$;
  """
)
