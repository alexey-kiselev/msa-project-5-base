from datetime import datetime, timedelta
from pathlib import Path
from airflow import DAG
from airflow.operators.email import EmailOperator
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.utils.trigger_rule import TriggerRule


def read_source(**context):
    lines = Path("/opt/airflow/data/orders.csv").read_text(encoding="utf-8").strip().splitlines()
    rows_count = len(lines) - 1
    context["ti"].xcom_push(key="rows_count", value=rows_count)
    print(f"read {rows_count} rows")
    return rows_count


def choose_branch(**context):
    rows_count = context["ti"].xcom_pull(task_ids="read_source", key="rows_count")
    if rows_count and rows_count >= 3:
        return "process_ok"
    return "process_skip"


def process_ok(**context):
    rows_count = context["ti"].xcom_pull(task_ids="read_source", key="rows_count")
    print(f"process branch: enough data ({rows_count} rows)")


def process_skip(**context):
    print("skip branch: not enough rows")


with DAG(
    dag_id="poc_dag",
    start_date=datetime(2026, 10, 12),
    schedule=None,
    catchup=False,
    tags=["poc"],
) as dag:
    read_source_task = PythonOperator(
        task_id="read_source",
        python_callable=read_source,
        retries=2,
        retry_delay=timedelta(seconds=10),
    )

    branch = BranchPythonOperator(
        task_id="branch_by_row_count",
        python_callable=choose_branch,
    )

    process_ok_task = PythonOperator(
        task_id="process_ok",
        python_callable=process_ok,
    )

    process_skip_task = PythonOperator(
        task_id="process_skip",
        python_callable=process_skip,
    )

    email_success = EmailOperator(
        task_id="email_success",
        to="ops@example.com",
        subject="poc_dag SUCCESS",
        html_content="<pre>Pipeline finished successfully.</pre>",
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
    )

    email_failure = EmailOperator(
        task_id="email_failure",
        to="ops@example.com",
        subject="poc_dag FAILED",
        html_content="<pre>Pipeline failed.</pre>",
        trigger_rule=TriggerRule.ONE_FAILED,
    )

    read_source_task >> branch
    branch >> [process_ok_task, process_skip_task]
    [process_ok_task, process_skip_task] >> email_success
    [process_ok_task, process_skip_task, read_source_task] >> email_failure
