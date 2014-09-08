<html>
<head>
    <style type="text/css">
        ${css}
        .right {
            float: right;
            padding-right:50px;
        }
        .bottom {
            position: fixed
            absolute:
        }
        .small {
            font-size: 8
        }

        .valign_up, .valign_bot {
            position:absolute;
        }
        .valign_up { left:130px; }
        .valign_bot { left:200px; }

        .cadre_bottom {
            padding: 4mm;
            margin: 4mm;
            border-width: thin;
            border-style: solid;
        }

    </style>
</head>
<body>
<%page expression_filter="entity"/>
<%
def carriage_returns(text):
    return text.replace('\n', '<br />')

def carrier_name(car_type):
    return car_type.replace('_', ' ').upper()

def pick(deposit):
    return deposit.picking_ids[0]

def cpny(deposit):
    return deposit.picking_ids[0].company_id

def tabulation(text):
    return text.replace('//t', '&nbsp; &nbsp; ')

%>
<%from datetime import date %>

%for deposit in objects:

<%block filter="carriage_returns, tabulation">
    SITE DE PRISE EN CHARGE:  ${cpny(deposit).colipostefr_support_city}
    <span class="right">BORDEREAU DE REMISE Offre Entreprises ${carrier_name(deposit.carrier_type)}</span>
    N° CLIENT<span class="valign_up">://t${deposit and cpny(deposit).colipostefr_account}</span> 
    <span class="right">EDITE LE ${formatLang(str(date.today()), date=True)}</span>
    LIBELLE CLIENT<span class="valign_up">://t${user.company_id.name}</span>
    N° BORDEREAU<span class="valign_up">://t${deposit.name} DU ${formatLang(deposit.create_date, date=True)}</span>

</%block>

    <% poids_total = 0 %>
    <% nombre_colis_total = 0 %>
    <table style="border:solid 1px" width="100%">
      <caption></caption>
      <tr align="left">
        <th>Réf. exped</th>
        <th>Nom et adresse<br />destinataire</th>
        <th>N° colis</th>
        <th class="small">CPOST</th>
        <th class="small">CPAYS</th>
        <th class="small">Poids<br />(KG)</th>
        <th>NM</th>
        <th>CRBT</th>
        <th>VA</th>
      </tr>
      %for line in deposit.picking_ids:
      <tr align="left">
          <td>${line.name}</td>
          <td>${line.partner_id.name or ''} ${line.partner_id.street or ''}</td>
          <td>${line.carrier_tracking_ref or ''}</td>
          <td>${line.partner_id.zip or ''}</td>
          <td>${line.partner_id.country_id and line.partner_id.country_id.code or 'FR'}</td>
          <td>${line.weight}</td>
          <td>${'1' or '0'}</td> <!-- TODO    #line.non_mecanisable and -->
          <td>000.00</td>
          <td>00</td>
      </tr>
        <% poids_total += line.weight %>
        <% nombre_colis_total += 1 %>
      %endfor
    </table>
    <%block filter="carriage_returns, tabulation">
    <div class="bottom_fixed">
        <table>
            <tr>
                <td style="width: 340px;">
    NOMBRE DE COLIS DE LA PAGE<span class="valign_bot">://t</span>
    POIDS DES COLIS DE LA PAGE<span class="valign_bot">://t${poids_page or '0'}</span>
    TOTAL CRBT EUR DE LA PAGE<span class="valign_bot">://t0.0</span>

    NOMBRE TOTAL DE COLIS<span class="valign_bot">://t${nombre_colis_total or '0'}</span>
    POIDS TOTAL DES COLIS<span class="valign_bot">://t${poids_total or '0'}</span>
    TOTAL CRBT EUR<span class="valign_bot">://t0.0</span>
    </div>
            </td>
            <td>
    <p style="width: 240px;" class="cadre_bottom">SIGNATURE DE L'AGENT (*) <br>
      <br>
      DATE
    </p>
    //t//t* Cette signature ne vaut pas validation des données
    //t//tindiquées par le client
            </td>
        </tr>
    </table>
    </%block>
    <p style="page-break-before: always" />

%endfor
</body>
</html>
