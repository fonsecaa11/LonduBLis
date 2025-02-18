<!-- EXECUTAR NO LIVE SERVER (XAMPP) -->
<?php
if (isset($_POST['executar'])) {
    // Configurações da base de dados MySQL
    $servername = "localhost";
    $username = "root";
    $password = "1234";
    $dbname = "projeto";

    // Criar a ligação à base de dados
    $conn = new mysqli($servername, $username, $password, $dbname);

    // Verificar a ligação
    if ($conn->connect_error) {
        die("Ligação falhou: " . $conn->connect_error);
    }

    // URL da página com as lojas
    $url = "https://feed.continente.pt/lojas";

    // Inicializar o cURL
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    $response = curl_exec($ch);
    curl_close($ch);

    // Verificar se o pedido foi bem-sucedido
    if (!$response) {
        die("Falha ao aceder ao site.");
    }

    // Limpar os dados da tabela
    $sql = "TRUNCATE TABLE lojas_continente";
    $conn->query($sql);

    // Carregar o HTML com DOMDocument
    $dom = new DOMDocument();
    @$dom->loadHTML($response);
    $xpath = new DOMXPath($dom);

    function limparEspacos($texto) {
        return preg_replace('/\s+/', ' ', trim($texto));
    }

    // Extrair dados das lojas
    $lojasNodes = $xpath->query("//li[contains(@class, 'storeMapHeader__store ')]");

    foreach ($lojasNodes as $lojaNode) {
        // Extrair o nome da loja
        $nome = $lojaNode->getAttribute("data-name");
        
        // Extrair a morada
        $enderecoNode = $xpath->query(".//p[contains(@class, 'storeMapHeader__store-addres')]", $lojaNode);
        $enderecoCompleto = $enderecoNode->length > 0 ? limparEspacos($enderecoNode->item(0)->textContent) : "N/A";

        if ($enderecoCompleto !== "N/A") {
            $regex = '/(.*?)(\d{4}-\d{3})(.*)/';
            if (preg_match($regex, $enderecoCompleto, $matches)) {
                $endereco = limparEspacos($matches[1]);
                $cp = $matches[2];
                $cidade = limparEspacos($matches[3]);
                $codigoPostal = $cp . " " . $cidade; // Unindo cidade e código postal
            } else {
                echo "Formato de endereço inválido: " . $enderecoCompleto . "<br>";
            }
        } else {
            echo "Endereço não encontrado para a loja: " . $nome . "<br>";
        }

        // Extrair as coordenadas
        $latitude = $lojaNode->getAttribute("data-lat");
        $longitude = $lojaNode->getAttribute("data-lng");
        
        // Inserir os dados na base de dados
        $stmt = $conn->prepare("INSERT INTO lojas_continente (endereco, nome, codigopostal, latitude, longitude) VALUES (?, ?, ?, ?, ?)");
        $stmt->bind_param("sssdd", $endereco, $nome, $codigoPostal, $latitude, $longitude);
        $stmt->execute();
    }

    // Fechar a ligação à base de dados
    $conn->close();

    echo "Dados extraídos e armazenados com sucesso!";
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Script Continente</title>
</head>
<body>
    <h1>Executar o Script para Inserir Lojas</h1>

    <form method="POST" action="">
        <button type="submit" name="executar">Executar Script</button>
    </form>
</body>
</html>