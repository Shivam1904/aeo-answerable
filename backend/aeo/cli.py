"""
CLI Interface.

This module uses Typer to provide a command-line interface for the AEO tool.
It handles user input, initializes the Crawler, and displays results using Rich.
"""
import typer
import asyncio
import json
from .config import Settings
from .crawler import Crawler
from rich.console import Console

app = typer.Typer()
console = Console()

@app.command()
def scan(
    url: str,
    max_pages: int = typer.Option(200, help="Max pages to scan"),
    mode: str = typer.Option("fast", help="Scan mode"),
    output: str = typer.Option("backend/output/aeo-report.json", help="Output JSON file")
):
    """
    Scan a website for AEO readiness.
    
    This command initializes the crawler, runs a BFS scan starting from the URL,
    and saves the results to a JSON file.
    
    Args:
        url (str): The seed URL to crawl.
        max_pages (int): Limit the number of pages to visit.
        mode (str): 'fast' (HTTP) or 'rendered' (Browser - future).
        output (str): Path to save the final JSON report.
    """
    # Ensure output directory exists
    import os
    output_dir = os.path.dirname(output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    console.print(f"[bold green]Starting scan for {url}[/bold green]")
    
    settings = Settings(
        start_url=url,
        max_pages=max_pages,
        mode=mode
    )
    
    import logging
    logging.basicConfig(level=logging.ERROR) # Reduce noise
    
    # Initialize Crawler based on mode
    if mode == "rendered":
        from .rendered_crawler import RenderedCrawler
        crawler = RenderedCrawler(settings)
        console.print("[bold magenta]Using Rendered Mode (Playwright)[/bold magenta]")
    else:
        crawler = Crawler(settings)
    
    # Run async scan with progress
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("[cyan]Crawling...", total=max_pages)
        
        # We need to hook into the crawler to update progress. 
        # Since we can't easily modify the crawler's internal loop without a callback or refactor,
        # we'll wrap the scan and just show a spinner/indeterminate progress or 
        # rely on the crawler's print statements (which might conflict with progress bar).
        # Better approach: The crawler runs fully async. 
        # For now, let's just show a spinner while it runs, as the crawler prints logs.
        
        # Actually, let's just run it. The original plan mentioned "manual progress update".
        # But `crawler.scan()` is a single awaitable. 
        # To get real progress, we'd need the crawler to yield status or update a shared object.
        # Given constraints, we will just use a status spinner.
        
        results = asyncio.run(crawler.scan())
        progress.update(task, completed=max_pages)
    
    console.print(f"\n[bold]Scan Complete![/bold]")
    console.print(f"Scanned: {results['summary']['scanned_count']} pages")
    console.print(f"Errors: {results['summary']['errors']}")
    
    # Display Audit Summary
    from rich.table import Table
    table = Table(title="Audit Results")
    table.add_column("URL", style="cyan", no_wrap=False)
    table.add_column("Struct Score", style="magenta")
    table.add_column("Clarity Score", style="green")
    table.add_column("Chunks", style="yellow")
    table.add_column("Consistency", style="blue")

    all_chunks = []
    for page in results['pages']:
        audits = page.get('audits', {})
        chunks_data = page.get('chunks', {})
        
        # Collect chunks for retrieval index
        if 'semantic' in chunks_data:
            all_chunks.extend(chunks_data['semantic'])

        struct_score = str(audits.get('structure', {}).get('score', '-'))
        clarity_score = str(audits.get('clarity', {}).get('score', '-'))
        
        sem_count = len(chunks_data.get('semantic', []))
        slid_count = len(chunks_data.get('sliding', []))
        consistency = str(chunks_data.get('consistency_score', '-'))
        
        table.add_row(
            page['url'], 
            struct_score, 
            clarity_score, 
            f"{sem_count}/{slid_count}",
            consistency
        )
        
    console.print(table)
    
    # Retrieval Simulation
    if all_chunks:
        from .retriever import LocalRetriever
        console.print(f"\n[bold yellow]Running Retrieval Simulation on {len(all_chunks)} chunks...[/bold yellow]")
        retriever = LocalRetriever()
        retriever.build_index(all_chunks)
        
        recall_stats = retriever.simulate_recall(results['pages'])
        
        console.print(f"Recall@1: {recall_stats.get('recall_at_1', '0.0')}")
        console.print(f"Recall@5: {recall_stats.get('recall_at_5', '0.0')}")
        console.print(f"Queries Simulated: {recall_stats.get('query_count', 0)}")
        
        # Add to results
        results['retrieval_stats'] = recall_stats

    with open(output, 'w') as f:
        json.dump(results, f, indent=2)
    
    console.print(f"Report saved to [bold]{output}[/bold]")

@app.command()
def init():
    """
    Create a default config file in the current directory.
    
    (Not Implemented Yet)
    """
    typer.echo("Config init not implemented yet.")

if __name__ == "__main__":
    app()
