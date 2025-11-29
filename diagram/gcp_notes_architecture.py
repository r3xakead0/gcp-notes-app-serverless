from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import Users
from diagrams.onprem.network import Internet
from diagrams.gcp.storage import Storage
from diagrams.gcp.compute import Functions
from diagrams.gcp.database import Firestore

# Crear el diagrama
with Diagram(
    "GCP Notes App Architecture",
    show=False,          # No abre el visor automáticamente
    filename="gcp-notes-architecture",
    direction="LR",      # Left -> Right
    graph_attr={"fontsize": "20", "fontname": "Times-Roman", "pad": "0.2"}, 
    outformat="png",
):
    user = Users("User\nBrowser")

    internet = Internet("Internet")

    with Cluster("Google Cloud Platform"):
        # Frontend
        static_site = Storage("Static Website\n(Cloud Storage)")

        # Backend
        api_function = Functions("Notes API\n(Cloud Functions)")

        # Base de datos
        db = Firestore("Notes\n(Firestore)")

    # Flujo: usuario -> internet -> sitio estático
    user >> Edge(label="HTTP/HTTPS\nGET") >> internet >> Edge(label="GET\nHTML/CSS/JS") >> static_site

    # Flujo: frontend JS -> API
    static_site >> Edge(label="Fetch\nREST /notes") >> api_function

    # Flujo: API -> Firestore
    api_function >> Edge(label="CRUD\nNotes") >> db