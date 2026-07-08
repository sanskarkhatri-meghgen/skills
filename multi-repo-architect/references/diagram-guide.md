# Diagram Guide — Draw.io Architecture Diagrams

## Overview

Produce two separate `.drawio` XML files (`mxGraphModel` format) to represent the architecture from two different perspectives:
1. **Low-Level Diagram (`low-level-diagram.drawio`)**: A logical service map.
2. **High-Level Diagram (`high-level-diagram.drawio`)**: A physical cloud infrastructure view.

Both files must use standard `mxfile` and `mxGraphModel` structure so they can be natively opened in draw.io or converted into a direct link.

---

## 1. Low-Level Diagram (Service Map)

**Rule: Use relevant service/vendor logos wherever possible.** Fall back to plain geometric shapes only when no logo exists for a component.

**Purpose**: Show every microservice with recognizable icons where available, connections as arrows, datastores as cylinders (or logo icons), queues as rounded rectangles (or logo icons).

### Shapes & Styles (Draw.io format)

**Service Box** (Frontend/Backend):
```xml
<mxCell id="service_id" value="frontend\n(Go / Gorilla)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1e3a5f;strokeColor=#3b82f6;fontColor=#ffffff;" vertex="1" parent="1">
  <mxGeometry x="{x}" y="{y}" width="140" height="60" as="geometry" />
</mxCell>
```
*Note: Use `\n` or HTML `<br>` for line breaks inside `value` if `html=1` is set.*

**Database / Datastore**:
```xml
<mxCell id="db_id" value="redis-cart\n(Memorystore)" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;fillColor=#3a2a1a;strokeColor=#f97316;fontColor=#ffffff;" vertex="1" parent="1">
  <mxGeometry x="{x}" y="{y}" width="100" height="80" as="geometry" />
</mxCell>
```

**Queue / Topic**:
```xml
<mxCell id="queue_id" value="order-events\n(SQS)" style="shape=step;perimeter=stepPerimeter;whiteSpace=wrap;html=1;fixedSize=1;fillColor=#2d1a3a;strokeColor=#a855f7;fontColor=#ffffff;" vertex="1" parent="1">
  <mxGeometry x="{x}" y="{y}" width="120" height="60" as="geometry" />
</mxCell>
```

**Edges / Connections**:
```xml
<mxCell id="edge_id" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="source_id" target="target_id">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

---

## 2. High-Level Diagram (Cloud Architecture)

**Rule: MUST use relevant cloud vendor icons and logos (AWS, GCP, Azure, etc.).**

**Purpose**: Show the physical cloud topology — VPC, subnets, managed services, compute clusters, and external SaaS integrations.

### Shapes & Styles (Draw.io format)

To use vendor icons in draw.io XML, set `shape=image` and provide the `image=` property with the standard draw.io stencil path. Here are common examples:

**AWS EC2 / Compute Instance**:
```xml
<mxCell id="ec2_id" value="EC2 Instances" style="shape=image;html=1;verticalAlign=top;verticalLabelPosition=bottom;labelBackgroundColor=#ffffff;imageAspect=0;aspect=fixed;image=img/lib/aws4/Compute/Amazon_EC2.svg;" vertex="1" parent="1">
  <mxGeometry x="{x}" y="{y}" width="60" height="60" as="geometry" />
</mxCell>
```

**AWS RDS / Database**:
```xml
<mxCell id="rds_id" value="PostgreSQL RDS" style="shape=image;html=1;verticalAlign=top;verticalLabelPosition=bottom;labelBackgroundColor=#ffffff;imageAspect=0;aspect=fixed;image=img/lib/aws4/Database/Amazon_RDS.svg;" vertex="1" parent="1">
  <mxGeometry x="{x}" y="{y}" width="60" height="60" as="geometry" />
</mxCell>
```

**Kubernetes Cluster (Universal)**:
```xml
<mxCell id="k8s_id" value="K8s Cluster" style="shape=image;html=1;verticalAlign=top;verticalLabelPosition=bottom;labelBackgroundColor=#ffffff;imageAspect=0;aspect=fixed;image=img/lib/mscae/Kubernetes.svg;" vertex="1" parent="1">
  <mxGeometry x="{x}" y="{y}" width="60" height="60" as="geometry" />
</mxCell>
```

**Database (Redis / Memcached)**:
```xml
<mxCell id="redis_id" value="Redis Cache" style="shape=image;html=1;verticalAlign=top;verticalLabelPosition=bottom;labelBackgroundColor=#ffffff;imageAspect=0;aspect=fixed;image=img/lib/mscae/Cache_Redis_Product.svg;" vertex="1" parent="1">
  <mxGeometry x="{x}" y="{y}" width="60" height="60" as="geometry" />
</mxCell>
```

**VPC Boundary / Container**:
```xml
<mxCell id="vpc_id" value="VPC Network" style="swimlane;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#3b82f6;strokeWidth=2;dashed=1;" vertex="1" parent="1">
  <mxGeometry x="{x}" y="{y}" width="800" height="500" as="geometry" />
</mxCell>
```

---

## 3. Icon Reference Table

Use these styles for common services. **GCP icons use stencil shapes** (loaded via `?libs=gcp2` in the URL). AWS and generic icons use direct SVG image paths.

### GCP Services (stencil-based — requires `?libs=gcp2` in URL)

Use `shape=mxgraph.gcp2.{ShapeName}` in the style. These are vector stencils, NOT image files.

| Service | Style to use |
|---|---|
| BigQuery | `shape=mxgraph.gcp2.BigQuery` |
| Cloud Storage | `shape=mxgraph.gcp2.Cloud Storage` |
| Cloud Pub/Sub | `shape=mxgraph.gcp2.Cloud PubSub` |
| Cloud Dataflow | `shape=mxgraph.gcp2.Cloud Dataflow` |
| Cloud KMS | `shape=mxgraph.gcp2.Key Management Service` |
| Cloud DLP | `shape=mxgraph.gcp2.Data Loss Prevention API` |
| GKE | `shape=mxgraph.gcp2.Container Engine` |
| Compute Engine | `shape=mxgraph.gcp2.Compute Engine` |
| App Engine | `shape=mxgraph.gcp2.App Engine` |
| Cloud SQL | `shape=mxgraph.gcp2.Cloud SQL` |

**GCP usage pattern:**
```xml
<mxCell id="bq_id" value="BigQuery" style="shape=mxgraph.gcp2.BigQuery;html=1;whiteSpace=wrap;" vertex="1" parent="1">
  <mxGeometry x="{x}" y="{y}" width="130" height="100" as="geometry" />
</mxCell>
```

### AWS Services (SVG image-based — always available)

| Service | draw.io `image=` path |
|---|---|
| AWS EC2 | `img/lib/aws4/Compute/Amazon_EC2.svg` |
| AWS RDS | `img/lib/aws4/Database/Amazon_RDS.svg` |
| AWS S3 | `img/lib/aws4/Storage/Amazon_Simple_Storage_Service.svg` |
| AWS SQS | `img/lib/aws4/Application_Integration/Amazon_Simple_Queue_Service.svg` |
| AWS Lambda | `img/lib/aws4/Compute/AWS_Lambda.svg` |
| AWS CloudFront | `img/lib/aws4/Networking_and_Content_Delivery/Amazon_CloudFront.svg` |

### Generic / Cross-Cloud (SVG image-based — always available)

| Service | draw.io `image=` path |
|---|---|
| Kubernetes | `img/lib/mscae/Kubernetes.svg` |
| Redis | `img/lib/mscae/Cache_Redis_Product.svg` |
| Docker | `img/lib/mscae/Docker.svg` |

**AWS / Generic usage pattern** (SVG images):
```xml
<mxCell id="k8s_id" value="K8s Cluster" style="shape=image;html=1;verticalAlign=top;verticalLabelPosition=bottom;labelBackgroundColor=none;imageAspect=0;aspect=fixed;image=img/lib/mscae/Kubernetes.svg;" vertex="1" parent="1">
  <mxGeometry x="{x}" y="{y}" width="60" height="60" as="geometry" />
</mxCell>
```

> **IMPORTANT**: GCP icons (`mxgraph.gcp2.*`) are stencils and MUST have `?libs=gcp2` in the draw.io URL. AWS icons (`img/lib/aws4/*`) and MSCAE icons (`img/lib/mscae/*`) are SVG images and work without any extra URL parameters.

---

## 4. Base XML Structure

Every generated `.drawio` file must wrap the cells in this standard `mxfile` structure:

```xml
<mxfile host="Electron" modified="2023-10-10T12:00:00.000Z" agent="Multi-Repo Architect" version="21.1.2" type="device">
  <diagram id="diagram_1" name="Architecture">
    <mxGraphModel dx="1000" dy="1000" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1600" pageHeight="900" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        
        <!-- Insert nodes and edges here. Be sure to specify unique IDs and basic x/y coordinates in mxGeometry -->
        
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```